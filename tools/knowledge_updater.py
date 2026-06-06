"""
knowledge_updater.py — smart-product-advisor

Crawls accessory roundup articles, product review sources, and e-commerce
bestseller lists, then appends new findings to SECOND-KNOWLEDGE-BRAIN.md.

Schedule: weekly cron (e.g., every Sunday at 02:00)
Usage: python tools/knowledge_updater.py [--category CATEGORY] [--dry-run]
"""

import asyncio
import hashlib
import json
import re
import sys
from datetime import date
from pathlib import Path
from typing import Optional

# crawl4ai is the primary fetching engine
try:
    from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
    CRAWL4AI_AVAILABLE = True
except ImportError:
    CRAWL4AI_AVAILABLE = False
    print("WARNING: crawl4ai not installed. Run: pip install crawl4ai")

BRAIN_FILE = Path(__file__).parent.parent / "SECOND-KNOWLEDGE-BRAIN.md"
DEDUP_FILE = Path(__file__).parent / ".knowledge_dedup_hashes.json"

TODAY = date.today().isoformat()

PRODUCT_CATEGORIES = [
    "smartphone",
    "laptop",
    "camera",
    "gaming_console",
    "tablet",
    "wireless_earbuds",
    "smartwatch",
    "desktop_pc",
]

SOURCES = [
    {
        "name": "Wirecutter",
        "base_url": "https://www.nytimes.com/wirecutter/",
        "query_template": "best accessories for {category}",
        "type": "review",
    },
    {
        "name": "PCMag",
        "base_url": "https://www.pcmag.com/",
        "query_template": "{category} accessories guide",
        "type": "review",
    },
    {
        "name": "RTings",
        "base_url": "https://www.rtings.com/",
        "query_template": "{category} accessories",
        "type": "specs",
    },
    {
        "name": "GSMArena",
        "base_url": "https://www.gsmarena.com/",
        "query_template": "{category} accessories",
        "type": "specs",
    },
]

SEARCH_QUERY_TEMPLATES = [
    "{category} best accessories {year}",
    "{category} must-have accessories",
    "{category} accessories buying guide",
    "what do you need with a {category}",
]


def load_dedup_hashes() -> set:
    if DEDUP_FILE.exists():
        with open(DEDUP_FILE, "r") as f:
            return set(json.load(f))
    return set()


def save_dedup_hashes(hashes: set) -> None:
    with open(DEDUP_FILE, "w") as f:
        json.dump(list(hashes), f, indent=2)


def url_hash(url: str) -> str:
    return hashlib.sha256(url.encode()).hexdigest()[:16]


def score_entry(title: str, category: str, date_str: str, recency_weight: float = 0.6, relevance_weight: float = 0.4) -> float:
    """Score an entry by recency + relevance (keyword match in title)."""
    year = date.today().year
    try:
        entry_year = int(date_str[:4])
        recency = max(0.0, 1.0 - (year - entry_year) * 0.2)
    except (ValueError, IndexError):
        recency = 0.5

    keywords = category.lower().split("_")
    title_lower = title.lower()
    keyword_hits = sum(1 for kw in keywords if kw in title_lower)
    relevance = min(1.0, keyword_hits / max(1, len(keywords)))

    return round(recency_weight * recency + relevance_weight * relevance, 3)


def parse_accessory_entries(content: str, category: str, source_name: str, source_url: str) -> list[dict]:
    """
    Extract accessory recommendation entries from crawled page content.
    Looks for product/item names in headings and list items.
    """
    entries = []

    lines = content.split("\n")
    current_item = None

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Detect item headings (## Best X, ### Top Y, **Bold Item**, numbered lists)
        heading_match = re.match(r'^#{1,4}\s+(.+)', line)
        bold_match = re.match(r'^\*\*(.+)\*\*', line)
        numbered_match = re.match(r'^\d+[\.\)]\s+(.+)', line)

        if heading_match:
            current_item = heading_match.group(1).strip()
        elif bold_match:
            current_item = bold_match.group(1).strip()
        elif numbered_match:
            current_item = numbered_match.group(1).strip()

        if current_item and len(current_item) > 5 and len(current_item) < 100:
            # Filter out obvious non-product lines
            skip_patterns = ["table of contents", "conclusion", "final thoughts", "frequently asked", "about the author"]
            if not any(p in current_item.lower() for p in skip_patterns):
                entry = {
                    "item": current_item,
                    "category": category,
                    "source_name": source_name,
                    "source_url": source_url,
                    "date": TODAY,
                    "score": score_entry(current_item, category, TODAY),
                }
                entries.append(entry)
                current_item = None

    # Deduplicate within this batch
    seen = set()
    unique_entries = []
    for e in entries:
        key = e["item"].lower()
        if key not in seen:
            seen.add(key)
            unique_entries.append(e)

    return unique_entries[:20]  # Cap at 20 items per source per category


async def crawl_source(url: str, category: str) -> str:
    """Fetch page content using crawl4ai."""
    if not CRAWL4AI_AVAILABLE:
        return ""
    try:
        config = CrawlerRunConfig(
            word_count_threshold=50,
            excluded_tags=["nav", "footer", "aside", "script", "style"],
            remove_overlay_elements=True,
        )
        async with AsyncWebCrawler() as crawler:
            result = await crawler.arun(url=url, config=config)
            return result.markdown if result.success else ""
    except Exception as e:
        print(f"  crawl4ai error for {url}: {e}")
        return ""


def format_brain_entry(entry: dict) -> str:
    """Format a single entry as a SECOND-KNOWLEDGE-BRAIN.md table row."""
    item = entry.get("item", "Unknown")
    category = entry.get("category", "unknown")
    why = entry.get("why_needed", "Common companion item")
    price = entry.get("avg_price", "varies")
    source = entry.get("source_url", "")
    date_added = entry.get("date", TODAY)
    return f"| {item} | {category} | {why} | {price} | {source} | {date_added} |"


def append_to_brain(new_entries: list[dict], dry_run: bool = False) -> int:
    """Append new entries to SECOND-KNOWLEDGE-BRAIN.md, skipping duplicates."""
    if not BRAIN_FILE.exists():
        print(f"ERROR: SECOND-KNOWLEDGE-BRAIN.md not found at {BRAIN_FILE}")
        return 0

    with open(BRAIN_FILE, "r", encoding="utf-8") as f:
        existing_content = f.read()

    hashes = load_dedup_hashes()
    appended = 0
    new_rows = []

    for entry in new_entries:
        h = url_hash(entry.get("source_url", "") + entry.get("item", ""))
        if h in hashes:
            continue
        row = format_brain_entry(entry)
        new_rows.append(row)
        hashes.add(h)
        appended += 1

    if not new_rows:
        print("No new entries to append (all duplicates).")
        return 0

    section_header = "\n### Auto-Updated Entries (knowledge_updater.py)\n\n| Item | Category | Why Needed | Avg Price | Source | Date Added |\n|------|----------|------------|-----------|--------|------------|\n"

    if "Auto-Updated Entries" in existing_content:
        # Find the table and append rows
        insert_point = existing_content.rfind("| Date Added |")
        if insert_point != -1:
            next_newline = existing_content.find("\n", insert_point)
            updated = (
                existing_content[: next_newline + 1]
                + "\n".join(new_rows)
                + "\n"
                + existing_content[next_newline + 1 :]
            )
        else:
            updated = existing_content + "\n".join(new_rows) + "\n"
    else:
        updated = existing_content + section_header + "\n".join(new_rows) + "\n"

    # Update the Knowledge Update Log
    log_entry = f"| {TODAY} | knowledge_updater.py (auto) | {appended} items | Weekly crawl |"
    if "| Date | Source |" in updated:
        updated = updated + log_entry + "\n"

    if not dry_run:
        with open(BRAIN_FILE, "w", encoding="utf-8") as f:
            f.write(updated)
        save_dedup_hashes(hashes)
        print(f"Appended {appended} new entries to SECOND-KNOWLEDGE-BRAIN.md")
    else:
        print(f"[DRY RUN] Would append {appended} entries:")
        for row in new_rows:
            print(f"  {row}")

    return appended


async def run_pipeline(categories: Optional[list] = None, dry_run: bool = False) -> None:
    """Main pipeline: crawl sources → extract entries → append to BRAIN."""
    if categories is None:
        categories = PRODUCT_CATEGORIES

    all_entries = []
    year = date.today().year

    print(f"Starting knowledge update pipeline for {len(categories)} categories...")

    for category in categories:
        print(f"\n[Category: {category}]")

        for source in SOURCES:
            query = source["query_template"].format(category=category, year=year)
            search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
            print(f"  Crawling: {source['name']} ({query})")

            content = await crawl_source(search_url, category)
            if content:
                entries = parse_accessory_entries(
                    content=content,
                    category=category,
                    source_name=source["name"],
                    source_url=source["base_url"],
                )
                print(f"    → Extracted {len(entries)} candidates")
                all_entries.extend(entries)
            else:
                print(f"    → No content retrieved")

    # Sort by score descending before appending
    all_entries.sort(key=lambda x: x.get("score", 0), reverse=True)

    total_appended = append_to_brain(all_entries, dry_run=dry_run)
    print(f"\nPipeline complete. Total new entries appended: {total_appended}")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Update SECOND-KNOWLEDGE-BRAIN.md for smart-product-advisor")
    parser.add_argument("--category", type=str, help="Limit update to a specific product category", default=None)
    parser.add_argument("--dry-run", action="store_true", help="Preview entries without writing to file")
    args = parser.parse_args()

    categories = [args.category] if args.category else None

    asyncio.run(run_pipeline(categories=categories, dry_run=args.dry_run))


if __name__ == "__main__":
    main()
