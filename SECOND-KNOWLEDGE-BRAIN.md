# SECOND-KNOWLEDGE-BRAIN.md — smart-product-advisor

> Self-improving domain knowledge base for Smart Product Companion & Upsell Recommendation.
> Updated by `tools/knowledge_updater.py` — do not edit the Auto-Updated sections manually.

---

## 1. Core Concepts & Frameworks

### Product Ecosystem Model
Every physical product exists within an ecosystem of:
- **Essential accessories** — items required for basic safe use (e.g., phone case for protection)
- **Functional accessories** — items that unlock a core use case (e.g., USB-C hub for laptop connectivity)
- **Comfort accessories** — items that enhance experience (e.g., wireless charger stand)
- **Luxury/status accessories** — premium upgrades (e.g., MagSafe wallet, designer case)

The harness maps each recommendation to one of these four layers, which maps to the three output tiers:
- Essential + Functional → "Essential" tier
- Comfort → "Nice-to-Have" tier
- Luxury/status → "Luxury" tier

### Compatibility Dimensions
Compatibility between a primary product and an accessory can fail along these axes:
1. **Physical fit** — form factor, port type, size (e.g., USB-A vs USB-C)
2. **Protocol compatibility** — charging protocol (PD, Qi, MagSafe), display protocol (Thunderbolt, HDMI)
3. **Software/ecosystem lock** — MFi certification (Apple), Works with Chromebook, Android Auto
4. **Regulatory** — CE, FCC, battery regulations (airlines, customs)

### Accessory Discovery Heuristics
1. **Category-based**: Every smartphone needs: protection, power, audio, connectivity
2. **Use-case-based**: Photography enthusiast also needs: storage, tripod, lighting, lens accessories
3. **Brand ecosystem**: Apple users → MFi certified; Samsung → Galaxy ecosystem; Sony → α-mount ecosystem
4. **Community wisdom**: Reddit, XDA-Developers, Photography forums surface real-world must-haves not covered in official guides

---

## 2. Key Research Papers

| Title | Authors | Year | Venue | DOI/Link | Relevance |
|-------|---------|------|-------|----------|-----------|
| Factorization Machines | Rendle, S. | 2010 | ICDM | https://ieeexplore.ieee.org/document/5694074 | Foundational model for product recommendation scoring |
| BPR: Bayesian Personalized Ranking from Implicit Feedback | Rendle et al. | 2009 | UAI | https://arxiv.org/abs/1205.2618 | Ranking algorithm applicable to accessory prioritization |
| Amazon.com Recommendations: Item-to-Item Collaborative Filtering | Linden et al. | 2003 | IEEE Internet Computing | https://doi.org/10.1109/MIC.2003.1167344 | "Frequently bought together" foundation |
| Deep Neural Networks for YouTube Recommendations | Covington et al. | 2016 | RecSys | https://dl.acm.org/doi/10.1145/2959100.2959190 | Neural retrieval + ranking for recommendations |
| Towards Explainable Product Recommendation | Chen et al. | 2019 | AAAI | https://ojs.aaai.org/index.php/AAAI/article/view/4813 | Explainability in recommendations — "why this accessory" |

---

## 3. State-of-the-Art Methods & Tools

### Recommendation Approaches
- **Content-Based Filtering:** Match accessory specs to primary product specs (port types, protocol versions, physical dimensions)
- **Collaborative Filtering:** "Users who bought X also bought Y" — e-commerce signal
- **Knowledge Graph Approach:** Model product–accessory relationships as a graph; traverse from product node to accessory nodes
- **LLM-Augmented Retrieval:** Use LLM to parse free-text product descriptions, extract structured specs, then match to accessory catalog

### Compatibility Verification Tools
- **GSMArena** — smartphone specs database (storage, ports, charging protocols)
- **PCPartPicker** — PC component compatibility engine
- **Rtings.com** — electronics performance + compatibility reviews
- **Manufacturer APIs** — Apple MFi program database, Samsung SmartThings compatibility

### Price Intelligence
- **Google Shopping API** — price lookup across retailers
- **CamelCamelCamel** — Amazon price history
- **PriceRunner, PriceSpy** — EU/UK multi-retailer comparison

---

## 4. Authoritative Data Sources

| Source | URL | Data Type | Update Frequency |
|--------|-----|-----------|-----------------|
| Wirecutter | https://www.nytimes.com/wirecutter/ | Expert-reviewed accessory roundups | Weekly |
| RTings | https://www.rtings.com/ | Electronics specs + compatibility | Ongoing |
| GSMArena | https://www.gsmarena.com/ | Smartphone specs database | Daily |
| PCMag | https://www.pcmag.com/ | Product reviews + accessory guides | Weekly |
| The Verge | https://www.theverge.com/ | Consumer electronics news + reviews | Daily |
| Amazon Best Sellers | https://www.amazon.com/best-sellers-electronics/ | Market popularity signal | Daily |
| Reddit r/gadgets | https://www.reddit.com/r/gadgets/ | Community recommendations | Real-time |
| Reddit r/buildapc | https://www.reddit.com/r/buildapc/ | PC accessory community knowledge | Real-time |
| Apple MFi | https://mfi.apple.com/ | Apple-certified accessory database | Monthly |

---

## 5. Analytical Frameworks (from Skill 7)

The following methods from `research-first-reasoning` (Skill 7) are applicable to smart-product-advisor:

| Method | Application in This Skill |
|--------|--------------------------|
| **Evidence Hierarchy** | Prefer compatibility claims from manufacturer specs > certified reviewer > community anecdote |
| **Multi-Criteria Decision Analysis (MCDA)** | The scoring matrix: Usefulness × Compatibility × Price-Value is an MCDA model |
| **Inversion / Pre-mortem** | "What would make this recommendation wrong?" — check for discontinued items, regional availability gaps |
| **First-Principles Decomposition** | Decompose product into its functional interfaces (ports, protocols, form factor) then match accessories to each interface |
| **Comparative Analysis** | When multiple accessories fill the same role, compare across features + price + compatibility score |
| **Source Triangulation** | Require ≥ 2 independent sources for Essential-tier items before including them |

---

## 6. Product Category Quick-Reference

### Smartphones
**Essential:** case, screen protector, charger (if not included), charging cable
**Nice-to-Have:** power bank, wireless charging pad, car mount, USB-C hub
**Luxury:** MagSafe wallet, wireless earbuds (premium), smartwatch (same ecosystem)

### Laptops
**Essential:** power adapter (if not included), laptop sleeve/bag
**Nice-to-Have:** USB-C hub/dock, external mouse, laptop stand, external SSD
**Luxury:** mechanical keyboard, external monitor, webcam upgrade

### Mirrorless/DSLR Cameras
**Essential:** extra batteries, memory cards (U3/V30+ rated), camera bag
**Nice-to-Have:** extra lenses, tripod, ND filters, lens cleaning kit
**Luxury:** gimbal stabilizer, external flash, drone for aerial shots

### Gaming Consoles
**Essential:** HDMI cable (if not included), extra controller
**Nice-to-Have:** gaming headset, extended storage (SSD/HDD), charging dock
**Luxury:** capture card, gaming chair, monitor upgrade

### Wireless Earbuds
**Essential:** replacement ear tips (if not in box)
**Nice-to-Have:** protective case, cable for wired mode (if applicable)
**Luxury:** DAC/amplifier (for audiophiles), ear tip variety pack

---

## 7. Self-Update Protocol

```yaml
crawl_sources:
  - url: https://www.nytimes.com/wirecutter/
    query_template: "best accessories for {product_category}"
    selector: article.review-list
  - url: https://www.rtings.com/
    query_template: "{product_model} accessories"
    selector: .score-section
  - url: https://www.gsmarena.com/
    query_template: "{product_model} specs"
    selector: .specs-list

search_queries:
  - "{product_category} best accessories {year}"
  - "{brand} {product} must-have accessories"
  - "{product_model} compatible accessories review"

update_frequency: weekly
dedup_method: url_hash
append_format: "| {item} | {category} | {why_needed} | {avg_price} | {source} | {date} |"
```

---

## 8. Knowledge Update Log

| Date | Source | Items Added | Notes |
|------|--------|-------------|-------|
| 2026-06-05 | Manual initialization | 45 items (product category quick-reference + papers + sources) | v1 baseline — pipeline not yet run |
