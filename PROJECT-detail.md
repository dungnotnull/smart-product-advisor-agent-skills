# PROJECT-detail.md — smart-product-advisor

## Executive Summary

`smart-product-advisor` is a Claude Code skill harness that transforms a single product name into a complete, ranked companion ecosystem. Given any primary product (phone, laptop, camera, gaming console, appliance, etc.), the harness researches the accessory landscape, verifies compatibility, scores each item by usefulness and value, and delivers a professional recommendation table — grouped by priority tier and backed by cited sources.

---

## Problem Statement

**Domain context:** Consumer electronics and general retail ecosystems are vast. A new phone owner needs a case, screen protector, fast charger, USB-C hub, power bank, wireless earbuds, car mount — but no store or manufacturer surfaces this complete picture at purchase time. Upsell recommendations from retailers are driven by margin, not user need. Review sites cover single categories (best phone cases, best power banks) but never synthesize across the full ecosystem of one product.

**Motivation:** Users waste money on incompatible accessories, miss essential items, and rediscover their needs piecemeal over weeks or months. A research-first, compatibility-verified, ranked recommendation list solves all three problems in one pass.

---

## Target Users & Use Cases

| User Type | Trigger | Skill Action |
|-----------|---------|--------------|
| Consumer — new device owner | "I just bought a Samsung Galaxy S25" | Surface essential + nice-to-have accessories ranked by priority |
| Consumer — gift buyer | "I'm buying a Sony A7 IV camera as a gift" | Return full photographer's companion kit |
| IT Manager | "We're deploying 50 Dell XPS 15 laptops" | Surface enterprise accessories: docking stations, cases, security locks |
| Gamer | "I have a PS5, what do I need?" | Surface controllers, headsets, storage, cooling stands, charging docks |
| Budget shopper | "I bought a Xiaomi 14T, budget under $100" | Filter recommendations to price range, prioritize essentials |

**Trigger examples:**
- "I just bought [product] — what else do I need?"
- "What accessories should I get for [product]?"
- "Recommend companion items for [product], budget $X"
- "I have [product], what will I probably need later?"

---

## Harness Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   smart-product-advisor                 │
│                       main.md                           │
└───────────────────────────┬─────────────────────────────┘
                            │
              ┌─────────────▼──────────────┐
              │   Stage 1: Product Intake  │
              │   Parse user input →       │
              │   product name/model/brand │
              └─────────────┬──────────────┘
                            │
              ┌─────────────▼──────────────────────┐
              │  sub-product-analyzer              │
              │  Inputs: product name/model        │
              │  Outputs: category, specs,         │
              │    brand ecosystem, use-case       │
              └─────────────┬──────────────────────┘
                            │
              ┌─────────────▼──────────────────────┐
              │  sub-accessory-researcher          │
              │  Inputs: product profile           │
              │  Outputs: candidate list (15–30)   │
              │    with item names + sources       │
              └─────────────┬──────────────────────┘
                            │
              ┌─────────────▼──────────────────────┐
              │  sub-compatibility-checker         │
              │  Inputs: candidate list + product  │
              │  Outputs: scored candidate list    │
              │    (High/Medium confidence only)   │
              └─────────────┬──────────────────────┘
                            │
              ┌─────────────▼──────────────────────┐
              │  sub-recommendation-ranker         │
              │  Inputs: scored candidates +       │
              │    optional price filter           │
              │  Outputs: final ranked, tiered     │
              │    recommendation list             │
              └─────────────┬──────────────────────┘
                            │
              ┌─────────────▼──────────────────────┐
              │  Quality Gate (inline in main.md)  │
              │  ✓ ≥ 5 recommendations             │
              │  ✓ All have compatibility score    │
              │  ✓ All have ≥ 1 cited source       │
              │  ✓ Price context provided          │
              └─────────────┬──────────────────────┘
                            │
              ┌─────────────▼──────────────────────┐
              │  Final Output                      │
              │  Ranked table, tiered by priority  │
              │  Essential / Nice-to-Have / Luxury │
              └────────────────────────────────────┘
```

---

## Full Sub-Skill Catalog

### sub-product-analyzer
- **Purpose:** Extract a structured product profile from the user's free-text input and WebSearch verification
- **Inputs:** Raw product name/model string from user
- **Outputs:** Structured profile — `{category, brand, model, key_specs[], ecosystem_brands[], primary_use_cases[]}`
- **Tools:** WebSearch, WebFetch
- **Quality gate:** Profile must contain category + at least 2 use cases before proceeding

### sub-accessory-researcher
- **Purpose:** Build a candidate list of companion items by searching expert reviews, e-commerce listings, and community recommendations
- **Inputs:** Product profile from sub-product-analyzer
- **Outputs:** Candidate list — array of `{item_name, item_category, why_needed, source_url}`
- **Tools:** WebSearch (queries: "[product] best accessories", "[product] must-have", "[product] accessory guide"), WebFetch
- **Quality gate:** ≥ 10 distinct candidates with sources before proceeding

### sub-compatibility-checker
- **Purpose:** Verify that each candidate accessory is actually compatible with the primary product
- **Inputs:** Candidate list + primary product profile
- **Outputs:** Scored candidate list — each item gains `{compatibility_confidence: High|Medium|Low, compatibility_notes}`; Low-confidence items without a source are dropped
- **Tools:** WebSearch ("[product] compatible with [accessory]"), WebFetch (manufacturer spec pages)
- **Quality gate:** No unscored items remain in the list

### sub-recommendation-ranker
- **Purpose:** Apply a multi-factor scoring matrix to produce a final, tiered, ranked recommendation list
- **Inputs:** Scored candidate list + optional user price range
- **Outputs:** Final ranked list — `{tier: Essential|Nice-to-Have|Luxury, rank, item_name, why_needed, compatibility_score, est_price_range, source}`
- **Tools:** None (pure scoring logic based on prior sub-skill outputs)
- **Scoring matrix:**
  - Usefulness: Essential=3, Nice-to-Have=2, Luxury=1
  - Compatibility: High=3, Medium=2 (Low items already dropped)
  - Price-Value: calculate from est_price vs user budget (if provided)
  - Final Score = Usefulness × Compatibility × Price-Value coefficient
- **Quality gate:** ≥ 5 items in final list; all tiers (Essential, Nice-to-Have, Luxury) represented if ≥ 9 items available

---

## Skill File Format Specification

### Frontmatter Schema
```yaml
---
name: smart-product-advisor
description: Research and rank companion items for any primary product; returns tiered recommendation table with compatibility scores and sources.
---
```

### Required Sections in main.md
1. `## Role & Persona` — domain expert shopper/product research analyst
2. `## Workflow (Harness Flow)` — numbered steps, references to sub-skills
3. `## Sub-skills Available` — list of all sub-skill files
4. `## Tools` — WebSearch, WebFetch, Read, Write, Skill
5. `## Output Format` — exact table structure
6. `## Quality Gates` — checklist that must pass before output is shown

---

## E2E Execution Flow

```
1. User invokes: /smart-product-advisor
2. Harness prompts: "What product did you recently buy or want to accessorize?"
3. User provides: product name/model/brand (and optionally a budget)
4. Stage 1 — Invoke sub-product-analyzer → receive product profile
5. Stage 2 — Invoke sub-accessory-researcher → receive candidate list
6. Stage 3 — Invoke sub-compatibility-checker → receive scored candidates
7. Stage 4 — Invoke sub-recommendation-ranker → receive final ranked list
8. Quality Gate check — if fails, loop back to Stage 2 with broader search queries
9. Render final output: tiered recommendation table
```

**Error handling:**
- If product is ambiguous (e.g., "the new phone"), ask for brand/model clarification before proceeding
- If fewer than 5 recommendations pass quality gate, broaden search to related product categories
- If WebSearch is unavailable, fall back to SECOND-KNOWLEDGE-BRAIN.md and signal limitation clearly

---

## SECOND-KNOWLEDGE-BRAIN Integration

- **Sources:** RTings, Wirecutter, PCMag, GSMArena, Amazon bestsellers by category, Reddit accessory threads
- **Crawl config:** Weekly; queries = "[product category] best accessories [year]", "[brand] compatible accessories"
- **Append format:** `| Item | Category | Why Needed | Avg Price | Source | Date Added |`
- **knowledge_updater.py schedule:** Weekly cron via system scheduler

---

## Quality Gates Definition

Before presenting the final output, all of the following must be true:

| Gate | Requirement |
|------|-------------|
| QG-1 | At least 5 final recommendations |
| QG-2 | Every recommendation has a compatibility confidence score |
| QG-3 | Every recommendation has at least one cited source URL |
| QG-4 | At least one "Essential" tier item is present |
| QG-5 | Price range context is provided for each item |
| QG-6 | Product profile was confirmed via WebSearch (not assumed from memory alone) |

---

## Test Scenarios

See `tests/test-scenarios.md` for 5+ concrete scenario tests.

---

## Key Design Decisions

1. **Research-first, not memory-first:** The harness always searches before generating. It never produces a recommendation list from training knowledge alone — WebSearch verification is mandatory for both product profile and accessory compatibility.
2. **Compatibility before ranking:** Items are compatibility-checked before scoring. This prevents recommending a USB-A hub to a MacBook Pro with only USB-C ports.
3. **Tiered output over flat lists:** Essential / Nice-to-Have / Luxury tiers make the output actionable for different budgets.
4. **Source citation required:** Every item must have a cited source. This prevents hallucinated accessory names or phantom compatibility claims.
5. **Price-range filter is optional, not required:** The skill works without a budget, but filters when one is provided — never silently dropping items without informing the user.
6. **Low-confidence items can survive if sourced:** Compatibility confidence = "Low" doesn't mean dropped — it means the item requires a source. This prevents over-filtering unusual but valid accessories.

---

## Cross-Skill API Contract

### Input Contract (what smart-product-advisor accepts)

| Field | Type | Required | Source | Description |
|-------|------|----------|--------|-------------|
| `product_name` | string | yes | User prompt | Primary product name (e.g., "iPhone 16 Pro Max") |
| `brand` | string | yes | User prompt or inference | Brand name (e.g., "Apple") |
| `model` | string | no | User prompt | Model identifier (e.g., "A3294") |
| `budget_usd` | number\|null | no | User prompt | Budget cap for price filtering |
| `evidence_mode` | boolean | no | User prompt | Enable Skill 7 deep evidence mode (default: false) |

### Output Contract (what smart-product-advisor emits)

**Format:** Tiered markdown tables with columns:
- `#`, `Item`, `Why You Need It / Why It Helps / What It Adds`, `Compat`, `Est. Price`, `Source`

**Data guarantees:**
- Essential tier always present with ≥ 1 item (if total ≥ 5 items)
- All prices in USD with ranges (e.g., "$15–$35")
- All items have a source URL
- Over-budget items are labeled `over_budget=true`, never silently dropped
- No items from the same product category as the primary device

### Cross-Skill Integration Points

**Invoking Skill 7 (research-first-reasoning):**
- **Hook point:** Between Step 3 (Accessory Research) and Step 4 (Compatibility Check)
- **Trigger:** `evidence_mode=true` or category is medical/safety-critical or item has single source
- **Data passed:** Array of `{item_name, source_url, why_needed}` for evidence verification
- **Data returned:** Same array enriched with `{evidence_level: high|medium|low, source_quality_score, cross_source_count}`
- **Output impact:** Extra `Evidence` column in Essential tier table

**Invoking Skill 6 (mental-health-guidance):**
- **Hook point:** After Step 2 (Product Analysis), before research begins
- **Trigger:** Product category in `[health, medical, fitness_tracker, wellness_device, sleep_aid]`
- **Data passed:** `{product_name, brand, model, category}`
- **Data returned:** `{safety_clear: boolean, advisory_message: string|null}`
- **Output impact:** Advisory warning box at top of output if safety flag raised

### Cross-Skill Constraints

| Constraint | Rule |
|------------|------|
| **No circular dependencies** | smart-product-advisor → Skill 7 (one-way). Skill 7 never calls smart-product-advisor. |
| **Optional integration** | Skill 7 is optional. Missing Skill 7 is not a quality gate failure. |
| **Fallback independence** | Fallback to SECOND-KNOWLEDGE-BRAIN.md works without any cross-skill integration. |
| **Version compatibility** | All cross-skill calls use JSON for structured data exchange. |

### Cross-Skill Output Stability

Output format is designed to be consumed by downstream skills. Stability guarantees:
- Column names and table structure are stable across versions
- New columns may be added (e.g., `Evidence` when Skill 7 is active) but never removed
- Source URLs use markdown link format: `[source_name](url)`
- Compatibility scores are always one of: `High`, `Medium`, `Low`
