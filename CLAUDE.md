# CLAUDE.md — Skill: smart-product-advisor

## Skill Identity
- **Name:** smart-product-advisor
- **Tagline:** Given any product you own, instantly surface the companion items you'll actually need — ranked by usefulness, compatibility, and value.
- **Domain:** Smart Product Companion & Upsell Recommendation
- **Current Phase:** Phase 1 — Core Sub-Skills

---

## Problem This Skill Solves

When a user purchases a primary product (phone, camera, laptop, gaming console, etc.), they rarely know upfront which accessories and companion items are essential versus optional. They end up discovering needs piecemeal — buying a phone and then realizing later they need a power bank, a case, a fast charger, a USB-C hub, screen protectors, etc. Each discovery costs time and often extra shipping. This skill proactively surfaces the full companion ecosystem for any product, ranked by urgency and utility, so the user can plan a complete purchase in one pass.

---

## Harness Flow Summary

```
User inputs primary product (name / model / brand / category)
  │
  ▼
Stage 1: sub-product-analyzer
  → Extract: category, brand ecosystem, specs, typical use-case profile
  │
  ▼
Stage 2: sub-accessory-researcher
  → WebSearch: common accessories, must-haves, nice-to-haves, expert roundups
  → Gather candidate list (15–30 items) with sources
  │
  ▼
Stage 3: sub-compatibility-checker
  → For each candidate: verify compatibility with primary product specs
  → Assign compatibility confidence score (High / Medium / Low)
  → Drop Low-confidence items without a source
  │
  ▼
Stage 4: sub-recommendation-ranker
  → Score each item: Usefulness Tier (Essential/Nice-to-Have/Luxury) × Compatibility × Price-Value
  → Apply optional price-range filter
  → Sort into final ranked list
  │
  ▼
Quality Gate (built into main.md)
  → ≥ 5 recommendations present
  → All items have a compatibility score
  → All items have at least one cited source
  → Price-range context provided
  │
  ▼
Final Output: Ranked recommendation table grouped by priority tier
```

---

## Sub-Skills

| File | Purpose |
|------|---------|
| `skills/sub-product-analyzer.md` | Extract product category, brand ecosystem, specs, and use-case profile from user input + WebSearch |
| `skills/sub-accessory-researcher.md` | Research companion items via WebSearch across e-commerce and expert review sources; return candidate list with sources |
| `skills/sub-compatibility-checker.md` | Verify each candidate item's compatibility with the primary product; assign confidence scores; drop unverifiable items |
| `skills/sub-recommendation-ranker.md` | Apply scoring matrix (Usefulness × Compatibility × Price-Value) to produce a final ranked, tiered recommendation list |

---

## Tools Required

- **WebSearch** — find accessories, reviews, compatibility specs
- **WebFetch** — deep-fetch product pages, review articles, e-commerce listings
- **Read / Write** — read sub-skill files, write final recommendation output
- **Skill** — invoke sub-skills at each harness stage
- **Bash** — run knowledge_updater.py when SECOND-KNOWLEDGE-BRAIN refresh is needed

---

## Knowledge Sources

- Google Shopping / Amazon product listings
- RTings, Wirecutter, PCMag, The Verge, GSMArena
- Reddit communities: r/buildapc, r/iphone, r/android, r/photography, r/gaming
- Manufacturer compatibility pages (Apple, Samsung, Sony, etc.)
- ArXiv: cs.IR (Information Retrieval), cs.HC (Human-Computer Interaction)

---

## Supporting Python Tools

| File | Purpose |
|------|---------|
| `tools/knowledge_updater.py` | crawl4ai pipeline — fetches latest accessory roundups, compatibility guides, and product ecosystem data; appends to SECOND-KNOWLEDGE-BRAIN.md |

---

## Active Development Tasks

### Phase 0–3: All Complete
- [x] Write CLAUDE.md
- [x] Write PROJECT-detail.md
- [x] Write PROJECT-DEVELOPMENT-PHASE-TRACKING.md
- [x] Write SECOND-KNOWLEDGE-BRAIN.md
- [x] Write skills/main.md
- [x] Write skills/sub-product-analyzer.md
- [x] Write skills/sub-accessory-researcher.md
- [x] Write skills/sub-compatibility-checker.md
- [x] Write skills/sub-recommendation-ranker.md
- [x] Write tools/knowledge_updater.py
- [x] Write tests/test-scenarios.md

### Phase 4: Testing & Validation ✅
- [x] tools/test_validator.py — automated structure & quality gate validation
- [x] tools/run_tests.py — test scenario runner with checklist tracker
- [x] tests/test-scenarios.md — 7 scenarios with detailed validation checklists

### Phase 5: Cross-Skill Integration ✅
- [x] Skills 7 (research-first-reasoning) integration hooks in main.md
- [x] Skills 6 (mental-health-guidance) safety check hook in main.md
- [x] Cross-skill API contract documented in PROJECT-detail.md

---

## Reference Files

- `PROJECT-detail.md` — full technical specification
- `PROJECT-DEVELOPMENT-PHASE-TRACKING.md` — phase roadmap
- `SECOND-KNOWLEDGE-BRAIN.md` — domain knowledge base
