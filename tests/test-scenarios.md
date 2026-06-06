# test-scenarios.md — smart-product-advisor

Each scenario tests a specific product type, budget combination, and harness code path. Run each scenario by invoking `/smart-product-advisor` and providing the stated input.

---

## Scenario 1 — Flagship Smartphone (No Budget)

**Input:**
```
Product: iPhone 16 Pro Max
Brand: Apple
Budget: none
```

**Expected Harness Behavior:**
- sub-product-analyzer returns: category=smartphone, port_types=[USB-C], charging_protocol=MagSafe, ecosystem_brands=[Apple]
- sub-accessory-researcher returns ≥ 12 candidates (protection, power, audio, connectivity categories)
- sub-compatibility-checker verifies MFi certification for charging accessories
- sub-recommendation-ranker places case + screen protector in Essential, MagSafe charger in Nice-to-Have, AirPods Pro in Luxury

**Pass Criteria:**
- [ ] QG-1: ≥ 5 recommendations
- [ ] QG-2: All items have compatibility score
- [ ] QG-3: All items have source URL
- [ ] QG-4: At least one Essential item present
- [ ] QG-5: All items have price range
- [ ] QG-6: Product verified via WebSearch (Apple.com or GSMArena)
- [ ] Case and screen protector appear in Essential tier
- [ ] No Android-only accessories appear in list

---

## Scenario 2 — Mid-Range Android Smartphone with Budget

**Input:**
```
Product: Samsung Galaxy A55
Brand: Samsung
Budget: $80
```

**Expected Harness Behavior:**
- sub-product-analyzer returns: category=smartphone, port_types=[USB-C], charging_protocol=USB-PD
- sub-recommendation-ranker applies $80 budget filter: items > $80 labeled over_budget=true, not dropped
- Essential tier contains items under $80
- Over-budget items are shown at bottom of each tier with label

**Pass Criteria:**
- [ ] All quality gates pass
- [ ] Items priced above $80 are labeled over_budget=true but still visible
- [ ] No item is silently dropped due to budget
- [ ] At least 2 Essential items are within the $80 budget

---

## Scenario 3 — Mirrorless Camera (Photography Use Case)

**Input:**
```
Product: Sony Alpha A7 IV
Brand: Sony
Budget: none
```

**Expected Harness Behavior:**
- sub-product-analyzer returns: category=camera, primary_use_cases=[photography, videography], ecosystem_brands=[Sony]
- sub-accessory-researcher uses photography use-case queries: "Sony A7 IV photography accessories", "Sony A7 IV must-have"
- Candidate list includes: extra batteries, memory cards (V60+ rated), camera bag, tripod, ND filters, lens cleaning kit
- sub-compatibility-checker verifies SD card speed class (V60 minimum for 4K recording)

**Pass Criteria:**
- [ ] All quality gates pass
- [ ] Memory cards have V60 or better speed class in compatibility_notes
- [ ] Extra batteries are in Essential tier (camera includes only 1)
- [ ] Camera bag appears in Essential or Nice-to-Have
- [ ] At least one lens accessory is present in Nice-to-Have or Luxury

---

## Scenario 4 — Gaming Console

**Input:**
```
Product: PlayStation 5
Brand: Sony
Budget: $150
```

**Expected Harness Behavior:**
- sub-product-analyzer returns: category=gaming_console, primary_use_cases=[gaming], port_types=[USB-A, USB-C, HDMI 2.1]
- sub-accessory-researcher returns: extra controller, gaming headset, SSD storage, HDMI cable, charging dock
- sub-compatibility-checker verifies PS5 NVMe SSD spec (PCIe 4.0 M.2) for storage accessories
- Items: PS5-compatible NVMe drives (~$120+) may be over_budget=true but still shown

**Pass Criteria:**
- [ ] All quality gates pass
- [ ] Extra DualSense controller appears (first-party preferred, or third-party with compatibility verified)
- [ ] SSD storage accessory includes compatibility_notes about PCIe 4.0 M.2 requirement
- [ ] HDMI cable included if "HDMI 2.1 required for 4K 120fps" is in notes
- [ ] Over-budget items are labeled but not hidden

---

## Scenario 5 — Laptop with Specific Work Use Case

**Input:**
```
Product: Apple MacBook Pro 14-inch M4 Pro
Brand: Apple
Budget: $200
```

**Expected Harness Behavior:**
- sub-product-analyzer returns: category=laptop, port_types=[Thunderbolt 4, MagSafe 3], ecosystem_brands=[Apple]
- sub-accessory-researcher uses "professional_work" use-case queries: "MacBook Pro 14 work from home accessories"
- Candidate list includes: USB-C hub/dock (Essential — MBP has limited ports), external SSD, laptop stand, wireless mouse
- sub-compatibility-checker verifies Thunderbolt 4 compatibility for docking stations

**Pass Criteria:**
- [ ] All quality gates pass
- [ ] USB-C/Thunderbolt hub/dock appears in Essential tier (M4 Pro MBP has only 3 Thunderbolt ports + 1 HDMI + SD card + MagSafe)
- [ ] Compatibility notes for dock explicitly mention Thunderbolt 4
- [ ] Laptop sleeve/bag appears in Essential or Nice-to-Have
- [ ] External SSD appears in Nice-to-Have
- [ ] Price filter applied: items > $200 labeled over_budget=true

---

## Scenario 6 — Ambiguous Input (Error Path Test)

**Input:**
```
Product: the new phone
Brand: not provided
```

**Expected Harness Behavior:**
- Harness detects ambiguous input (no brand/model)
- Asks clarifying question: "Which brand and model is your phone?"
- Does NOT proceed to sub-product-analyzer until clarification received

**Pass Criteria:**
- [ ] Harness does not generate a recommendation list for the ambiguous input
- [ ] A single clarifying question is asked (not multiple questions at once)
- [ ] After clarification, harness proceeds normally and all quality gates pass

---

## Scenario 7 — Fallback Path Test (WebSearch Unavailable)

**Input:**
```
Product: Samsung Galaxy S25 Ultra
Brand: Samsung
Budget: none
[Simulate: WebSearch tool unavailable]
```

**Expected Harness Behavior:**
- Harness detects WebSearch failure
- Falls back to SECOND-KNOWLEDGE-BRAIN.md "Product Category Quick-Reference" for smartphones
- Prepends fallback notice to output: "NOTE: WebSearch was unavailable. Recommendations are based on internal knowledge base..."
- Still produces ≥ 5 recommendations from BRAIN

**Pass Criteria:**
- [ ] Fallback notice is shown at top of output
- [ ] ≥ 5 recommendations are produced from internal knowledge
- [ ] Compatibility scores are labeled as "based on category defaults" since live verification was unavailable
- [ ] No hallucinated source URLs in output (source = "SECOND-KNOWLEDGE-BRAIN.md, v1")

---

## Quality Gate Summary Table

| QG | Requirement | Tested In |
|----|------------|-----------|
| QG-1 | ≥ 5 recommendations | All scenarios |
| QG-2 | All items have compatibility score | Scenarios 1, 3, 4, 5 |
| QG-3 | All items have source URL | Scenarios 1, 2, 5 |
| QG-4 | At least one Essential item | All scenarios |
| QG-5 | All items have price range | Scenarios 2, 4, 5 |
| QG-6 | Product verified via WebSearch | Scenarios 1, 3, 4 |
| Fallback | WebSearch-unavailable path works | Scenario 7 |
| Clarification | Ambiguous input triggers clarification | Scenario 6 |
| Budget | Over-budget items labeled, not dropped | Scenarios 2, 4, 5 |
| Ecosystem | Apple MFi / Samsung / Sony checks | Scenarios 1, 3, 4 |
