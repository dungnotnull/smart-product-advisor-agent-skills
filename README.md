# Smart Product Advisor — Agent Skill

> *Given any product you own or just bought, instantly discover the companion items you'll actually need — ranked by usefulness, compatibility, and value.*

[![Agent Skill](https://img.shields.io/badge/Claude-Code_Skill-8A2BE2?logo=claude&logoColor=white)](https://github.com/dungnotnull/smart-product-advisor-agent-skills)
[![Phases](https://img.shields.io/badge/status-complete-2ea44f)](#)
[![License](https://img.shields.io/badge/license-MIT-blue)](#)

---

## What It Does

When you buy a new product — phone, laptop, camera, gaming console, anything — you rarely know upfront which accessories are essential versus optional. This skill surfaces the **full companion ecosystem** in one pass:

- 🔍 **Researches** expert reviews and community recommendations
- ✅ **Verifies** compatibility with your specific product model
- 🏆 **Ranks** every item by usefulness × compatibility × value
- 💰 **Respects** your budget (optional) — over-budget items are labeled, never hidden

### Example

```
/smart-product-advisor
→ "I just bought an iPhone 16 Pro Max"
```

| Tier | Items |
|------|-------|
| **Essential** | Case, screen protector, MagSafe charger |
| **Nice-to-Have** | Power bank, USB-C hub, wireless charging stand |
| **Luxury** | AirPods Pro, MagSafe wallet |

---

## How It Works

The skill runs a **4-stage harness** — each stage is an independent sub-skill with its own quality gates.

```
┌─────────────────────────────────────────────────────────┐
│                   smart-product-advisor                 │
│                       main.md                           │
└───────────────────────────┬─────────────────────────────┘
                            │
              ┌─────────────▼──────────────┐
              │   Stage 1: Product Intake  │  Parse product name, brand, budget
              └─────────────┬──────────────┘
                            │
              ┌─────────────▼──────────────────────┐
              │  sub-product-analyzer              │  Extract structured profile
              │  → category, specs, use-cases       │  (category, ports, ecosystem)
              └─────────────┬──────────────────────┘
                            │
              ┌─────────────▼──────────────────────┐
              │  sub-accessory-researcher          │  Build candidate list (15–30)
              │  → expert reviews, communities,     │  across Protection, Power,
              │    e-commerce                       │  Audio, Storage, etc.
              └─────────────┬──────────────────────┘
                            │
              ┌─────────────▼──────────────────────┐
              │  sub-compatibility-checker         │  Score each item as
              │  → physical fit, protocols,         │  High / Medium / Low
              │    ecosystem locks                  │  confidence
              └─────────────┬──────────────────────┘
                            │
              ┌─────────────▼──────────────────────┐
              │  sub-recommendation-ranker         │  Score = Usefulness ×
              │  → multi-factor scoring matrix      │  Compatibility × Price-Value
              └─────────────┬──────────────────────┘
                            │
              ┌─────────────▼──────────────────────┐
              │  Quality Gate (6 checks)           │  ✓ ≥5 items  ✓ Compat scores
              │  → no output until all pass         │  ✓ Sources   ✓ Essential tier
              └─────────────┬──────────────────────┘
                            │
              ┌─────────────▼──────────────────────┐
              │  Final Output                      │  Ranked tables grouped by
              │  Essential / Nice-to-Have / Luxury  │  priority tier
              └────────────────────────────────────┘
```

### Quality Gates

| Gate | Requirement | Recovery |
|------|-------------|----------|
| QG-1 | ≥ 5 recommendations | Broaden search, re-run Stage 2 |
| QG-2 | Every item has compatibility score | Re-check missing items |
| QG-3 | Every item has a source URL | Re-check missing items |
| QG-4 | At least one Essential item | Verify tier assignment |
| QG-5 | Every item has price range | Quick WebSearch for prices |
| QG-6 | Product confirmed via WebSearch | Search specs before proceeding |

---

## Files

```
smart-product-advisor-skill/
├── skills/
│   ├── main.md                          # Harness orchestration (entry point)
│   ├── sub-product-analyzer.md          # Stage 1: Product profiling
│   ├── sub-accessory-researcher.md      # Stage 2: Accessory discovery
│   ├── sub-compatibility-checker.md     # Stage 3: Compatibility scoring
│   └── sub-recommendation-ranker.md     # Stage 4: Ranking & tiering
├── tools/
│   ├── knowledge_updater.py             # Crawl4AI pipeline for SECOND-KNOWLEDGE-BRAIN
│   ├── test_validator.py                # Automated structure & quality gate validation
│   └── run_tests.py                     # Test scenario runner with checklist tracker
├── tests/
│   └── test-scenarios.md                # 7 test scenarios with pass criteria
├── SECOND-KNOWLEDGE-BRAIN.md            # Self-improving domain knowledge base
├── PROJECT-detail.md                    # Full technical specification
├── PROJECT-DEVELOPMENT-PHASE-TRACKING.md # Phase roadmap
├── CLAUDE.md                            # Agent identity file
├── README.md                            # This file
└── .gitignore
```

---

## Usage

Invoke from Claude Code:

```
/smart-product-advisor
```

The harness will prompt you:

> *What product did you recently buy or want to accessorize? Please share the brand and model if you know it. Do you have a budget in mind?*

Provide a product (optionally with budget):

```
Product: Sony Alpha A7 IV
Brand: Sony
Budget: none
```

Or with a budget constraint:

```
Product: Samsung Galaxy A55
Brand: Samsung
Budget: $80
```

### Cross-Skill Features

- **Deep evidence mode**: Pass `evidence_mode: true` to invoke `research-first-reasoning` (Skill 7) for source quality scoring and cross-source triangulation on every item.
- **Health/medical safety check**: If the product category is health-related, a safety validation runs automatically via `mental-health-guidance` (Skill 6).

---

## Fallback Behavior

If **WebSearch** is unavailable, the skill falls back to `SECOND-KNOWLEDGE-BRAIN.md` — a self-improving knowledge base populated by the weekly `knowledge_updater.py` pipeline. A notice is prepended to the output:

```
> NOTE: WebSearch was unavailable. Recommendations are based on internal
> knowledge base (last updated: 2026-06-05). Verify compatibility independently.
```

---

## Development

### Running Tests

```bash
# Validate skill file structure and quality gate consistency
python tools/test_validator.py all

# List all test scenarios with validation checklists
python -X utf8 tools/run_tests.py --list

# Initialize a test progress report
python -X utf8 tools/run_tests.py --report
```

### Updating the Knowledge Base

```bash
# Full crawl across all product categories (weekly cron)
python tools/knowledge_updater.py

# Single category (e.g., smartphones)
python tools/knowledge_updater.py --category smartphone

# Preview without writing
python tools/knowledge_updater.py --category laptop --dry-run
```

### Architecture Validation

`test_validator.py` runs 12 checks automatically:
- File existence & frontmatter validity
- Required sections per sub-skill
- Sub-skill cross-references in main harness
- Output format tiers (Essential / Nice-to-Have / Luxury)
- Fallback logic & clarification prompts
- Knowledge updater completeness (crawl4ai, dedup, scoring, CLI)
- Test scenario coverage (7 scenarios, budget + fallback paths)
- All 6 quality gates defined in main.md and test-scenarios.md
- Sub-skill quality gate consistency

---

## Design Principles

1. **Research-first, not memory-first** — never generates from training knowledge alone
2. **Compatibility before ranking** — items scored before prioritized
3. **Tiered output** — Essential / Nice-to-Have / Luxury makes it actionable
4. **Source citation required** — prevents hallucinated accessories
5. **Price filter is a label, not a silencer** — over-budget items shown, never dropped
6. **Low-confidence items can survive with sources** — prevents over-filtering

---

## Built With

- **Claude Code** — Agent skill framework
- **crawl4ai** — Web crawling for knowledge base updates
- **Python 3** — Automation & validation tooling

---

## Authors

- **Dung Nguyen** — [@dungnotnull](https://github.com/dungnotnull)
- **Claude** — AI pair programmer (Anthropic)

---

*Part of the [Claude Code Skill Library](https://github.com/dungnotnull/smart-product-advisor-agent-skills).*
