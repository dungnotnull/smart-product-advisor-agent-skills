# PROJECT-DEVELOPMENT-PHASE-TRACKING.md — smart-product-advisor

## Overview

| Phase | Name | Timeline | Status |
|-------|------|----------|--------|
| 0 | Research & Skill Architecture | Week 1–2 | Complete |
| 1 | Core Sub-Skills | Week 3–5 | Complete |
| 2 | Main Harness + Quality Gates | Week 6–8 | Complete |
| 3 | SECOND-KNOWLEDGE-BRAIN Pipeline | Week 9–10 | Complete |
| 4 | Testing & Validation | Week 11–12 | Complete |
| 5 | Integration & Cross-Skill Wiring | Week 13–14 | Complete |

---

## Phase 0 — Research & Skill Architecture (Week 1–2)

**Goal:** Understand the domain, define harness stages, identify sub-skills.

### Tasks
- [x] Read product recommendation and e-commerce research literature
- [x] Survey existing accessory recommendation patterns (Amazon "frequently bought together", Wirecutter guides)
- [x] Define the 4-stage harness: Analyze → Research → Check → Rank
- [x] Identify required sub-skills: product-analyzer, accessory-researcher, compatibility-checker, recommendation-ranker
- [x] Populate SECOND-KNOWLEDGE-BRAIN.md with foundational domain knowledge

### Deliverables
- CLAUDE.md skeleton
- SECOND-KNOWLEDGE-BRAIN.md v1

### Success Criteria
- Harness stages clearly defined with input/output contracts
- At least 3 sub-skills identified with distinct responsibilities

---

## Phase 1 — Core Sub-Skills (Week 3–5)

**Goal:** Implement the 4 sub-skill files.

### Tasks
- [x] Write `skills/sub-product-analyzer.md`
- [x] Write `skills/sub-accessory-researcher.md`
- [x] Write `skills/sub-compatibility-checker.md`
- [x] Write `skills/sub-recommendation-ranker.md`
- [x] Define quality gates per sub-skill (min outputs, required fields)

### Deliverables
- 4 sub-skill files under `skills/`

### Success Criteria
- Each sub-skill has: Role, Workflow, Inputs, Outputs, Tools, Quality Gate
- Input/output contracts are consistent across the chain

### Estimated Effort
- 2–3 hours per sub-skill file × 4 = 8–12 hours

---

## Phase 2 — Main Harness + Quality Gates (Week 6–8)

**Goal:** Wire the sub-skills into the main harness with orchestration logic and global quality gates.

### Tasks
- [x] Write `skills/main.md` — full harness orchestration
- [x] Implement global Quality Gate checklist (QG-1 through QG-6)
- [x] Add error handling: ambiguous product → clarification prompt
- [x] Add fallback path: if WebSearch unavailable → SECOND-KNOWLEDGE-BRAIN
- [x] Add price-range filter integration in ranker stage

### Deliverables
- `skills/main.md`

### Success Criteria
- Full harness runs from user input to final output in a single `/smart-product-advisor` invocation
- All 6 quality gates implemented
- Error paths tested for: ambiguous input, WebSearch failure, <5 candidates

### Estimated Effort
- 4–6 hours

---

## Phase 3 — SECOND-KNOWLEDGE-BRAIN Pipeline (Week 9–10)

**Goal:** Build the automated knowledge updater so the skill's domain knowledge grows over time.

### Tasks
- [x] Write `tools/knowledge_updater.py`
- [x] Implement crawl4ai pipeline for: RTings, Wirecutter, PCMag, GSMArena
- [x] Implement WebSearch queries for "[product category] best accessories [year]"
- [x] Implement deduplication logic (URL hash check)
- [x] Implement scoring (recency + relevance) for appended entries
- [x] Test pipeline against 3 product categories (smartphones, laptops, cameras)

### Deliverables
- `tools/knowledge_updater.py`
- SECOND-KNOWLEDGE-BRAIN.md v2 (with pipeline-populated entries)

### Success Criteria
- Pipeline runs without errors
- Appended entries follow the defined format
- Deduplication prevents duplicate entries across runs
- At least 20 new entries added per weekly run across 3+ categories

### Estimated Effort
- 6–8 hours

---

## Phase 4 — Testing & Validation (Week 11–12)

**Goal:** Validate skill correctness and output quality across diverse product types.

### Tasks
- [x] Run all 5+ test scenarios from `tests/test-scenarios.md`
- [x] Verify all 6 quality gates pass for each scenario
- [x] Check recommendation accuracy: are Essential items actually essential?
- [x] Check compatibility: verify no incompatible items appear in final output
- [x] Stress-test with obscure products (niche camera model, legacy console, industrial device)
- [x] Validate fallback path (disable WebSearch, confirm SECOND-KNOWLEDGE-BRAIN fallback works)
- [x] Validate price-range filter: confirm items above budget are labeled, not silently dropped

### Deliverables
- Test run logs (in tests/test-scenarios.md, annotated)
- Bug list and fixes
- `tools/test_validator.py` — automated skill structure & quality gate validation
- `tools/run_tests.py` — test scenario runner with JSON report tracking

### Success Criteria
- [x] All 5 core scenarios pass
- [x] No hallucinated product names or phantom compatibility claims
- [x] Price filter works correctly for 3 budget levels ($0–50, $50–150, $150+)

### Estimated Effort
- 4–6 hours

---

## Phase 5 — Integration & Cross-Skill Wiring (Week 13–14)

**Goal:** Wire smart-product-advisor into the broader Claude Skill Library ecosystem.

### Tasks
- [x] Integrate `research-first-reasoning` (Skill 7) as optional sub-skill for deeper evidence-based verification
- [x] Add import hook: if product is in health/medical category → invoke `mental-health-guidance` safety check (Skill 6)
- [x] Ensure consistent output format compatible with any downstream skill that consumes recommendation lists
- [x] Document cross-skill API contract: inputs accepted, outputs emitted

### Deliverables
- Updated `skills/main.md` with cross-skill invocation hooks
- Cross-skill API spec in PROJECT-detail.md

### Success Criteria
- [x] `/smart-product-advisor` can optionally call `research-first-reasoning` for higher-confidence outputs
- [x] No circular dependencies between skills
- [x] Output format is stable and documented

### Estimated Effort
- 3–4 hours

---

## Milestones Summary

| Milestone | Target Date | Criteria |
|-----------|-------------|----------|
| M1: Architecture defined | Week 2 | Harness stages + sub-skill contracts documented |
| M2: Sub-skills complete | Week 5 | 4 sub-skill files written and internally consistent |
| M3: Main harness working | Week 8 | Full E2E run from input to final output |
| M4: Knowledge pipeline live | Week 10 | knowledge_updater.py running and populating BRAIN |
| M5: All tests pass | Week 12 | 5+ scenarios pass all quality gates; test_validator.py + run_tests.py operational |
| M6: Cross-skill wired | Week 14 | Skill 7 integration confirmed; cross-skill API contract documented in PROJECT-detail.md and main.md |
