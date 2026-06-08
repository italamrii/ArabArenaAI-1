# Data Acquisition Plan — ArabArenaAI-1

**Phase 3.5 — Strategy only.** No data collection, downloads, scrapers, or training pipelines in this phase.

This document identifies the **top 20 candidate datasets**, tiers them, defines a **weighted acquisition framework**, and maps a **collection roadmap** (Phases A–E) aligned with ADR-004 Saudi-first knowledge strategy.

Related: [DATA_MOAT_STRATEGY.md](DATA_MOAT_STRATEGY.md) · [DATA_RISKS.md](DATA_RISKS.md) · [DATA_TARGETS.md](DATA_TARGETS.md) · [LICENSING_GUIDE.md](LICENSING_GUIDE.md) · [DATA_PIPELINE.md](DATA_PIPELINE.md)

---

## Mission Alignment

| Principle | Acquisition implication |
|-----------|-------------------------|
| **Saudi-first** | Tier 1 dominated by KSA government, policy, and business sources |
| **GCC-aware** | Tier 2 includes GCC economic and dialect corpora |
| **Arabic-first** | Arabic quality weighted heavily; no English-only bulk ingest |
| **Business-aware** | ZATCA, MISA, Tadawul, chambers, procurement in early phases |
| **Developer-friendly** | Programming corpora in Phase D — regression guard, not primary moat |

**Competitive thesis:** Win on **licensed, curated, Saudi-weighted knowledge** — not raw crawl volume or model parameter count.

---

## Top 20 Candidate Datasets (Ranked)

Scores use the [Priority Formula](#weighted-acquisition-framework) below. **Verify all licenses at ingest time** — classes are planning estimates.

| Rank | Name | Tier | Priority | License |
|------|------|------|----------|---------|
| 1 | Vision 2030 Official Publications | 1 | **92** | L1 |
| 2 | Saudi Open Data Portal (curated subsets) | 1 | **87** | L1 |
| 3 | Saudi Ministry of Culture — Heritage & Public Content | 1 | **85** | L1 |
| 4 | MISA Investment & Business Setup Guides | 1 | **83** | L1 |
| 5 | Government Digital Services Public Documentation | 1 | **84** | L2 |
| 6 | ZATCA Tax & E-Invoicing Guidance | 1 | **83** | L1 |
| 7 | Monsha'at / Chambers SME & Entrepreneurship Content | 1 | **80** | L2 |
| 8 | Arabic Wikipedia (SA/GCC filtered) | 2 | **78** | L2 |
| 9 | Saudi Exchange (Tadawul) Public Disclosures | 2 | **77** | L2 |
| 10 | Etimad Government Procurement Public Docs | 2 | **77** | L2 |
| 11 | MADAR Corpus (Gulf / Saudi dialect subset) | 2 | **77** | L2 |
| 12 | Partner-Licensed Business Correspondence | 2 | **72** | L3 |
| 13 | GCC Economic & Trade Public Reports | 2 | **71** | L1 |
| 14 | Open Academic Arabic Text (research corpora) | 2 | **68** | L2 |
| 15 | UN Parallel Corpus (Arabic–English) | 3 | **69** | L1 |
| 16 | Licensed Regional Arabic News Archive | 3 | **67** | L3 |
| 17 | OSCAR Arabic (heavy quality filter) | 3 | **60** | L1 |
| 18 | Arabic Developer Q&A (Stack Overflow mirrors) | 3 | **59** | L2 |
| 19 | The Stack / OSS Code (Arabic signal filter) | 3 | **51** | L1 |
| 20 | Common Crawl Arabic (aggressive filter) | 3 | **51** | L1 |

---

## Dataset Catalog (Full Detail)

### 1. Vision 2030 Official Publications

| Field | Value |
|-------|-------|
| **Source** | Vision 2030 official portal & affiliated program sites |
| **Source URL** | https://www.vision2030.gov.sa/ |
| **Country** | SA |
| **Language** | ar-SA (primary), en (filter/tag) |
| **Domain** | government / policy |
| **License Class** | L1 |
| **Estimated Size** | 50–200 MB text (extracted) |
| **Collection Difficulty** | 35 / 100 |
| **Saudi Relevance** | 98 |
| **Arabic Relevance** | 95 |
| **Business Relevance** | 70 |
| **Technical Relevance** | 20 |
| **Strategic Value** | 95 |
| **Priority Score** | **92** |
| **Tier** | **1** |
| **Notes** | Core Saudi knowledge; PDF extraction; date-stamp all documents. Manifest: `vision2030.yaml`. |

---

### 2. Saudi Open Data Portal (Curated Subsets)

| Field | Value |
|-------|-------|
| **Source** | Saudi Open Data Portal |
| **Source URL** | https://data.gov.sa/ |
| **Country** | SA |
| **Language** | ar-SA, mixed |
| **Domain** | government / statistics |
| **License Class** | L1 (per-dataset verification) |
| **Estimated Size** | 500 MB–5 GB (subset TBD) |
| **Collection Difficulty** | 45 / 100 |
| **Saudi Relevance** | 95 |
| **Arabic Relevance** | 85 |
| **Business Relevance** | 75 |
| **Technical Relevance** | 30 |
| **Strategic Value** | 92 |
| **Priority Score** | **87** |
| **Tier** | **1** |
| **Notes** | Child manifest per dataset; no bulk ingest without per-source L-class. |

---

### 3. Saudi Ministry of Culture — Heritage & Public Content

| Field | Value |
|-------|-------|
| **Source** | Ministry of Culture public publications |
| **Source URL** | https://www.moc.gov.sa/ |
| **Country** | SA |
| **Language** | ar-SA |
| **Domain** | culture / heritage |
| **License Class** | L1 |
| **Estimated Size** | 20–100 MB |
| **Collection Difficulty** | 40 / 100 |
| **Saudi Relevance** | 90 |
| **Arabic Relevance** | 92 |
| **Business Relevance** | 35 |
| **Technical Relevance** | 15 |
| **Strategic Value** | 75 |
| **Priority Score** | **85** |
| **Tier** | **1** |
| **Notes** | Cultural fluency; etiquette and national identity context. |

---

### 4. MISA Investment & Business Setup Guides

| Field | Value |
|-------|-------|
| **Source** | Ministry of Investment (MISA) |
| **Source URL** | https://misa.gov.sa/ |
| **Country** | SA |
| **Language** | ar-SA, en |
| **Domain** | business / investment |
| **License Class** | L1 |
| **Estimated Size** | 30–150 MB |
| **Collection Difficulty** | 38 / 100 |
| **Saudi Relevance** | 90 |
| **Arabic Relevance** | 85 |
| **Business Relevance** | 95 |
| **Technical Relevance** | 30 |
| **Strategic Value** | 88 |
| **Priority Score** | **83** |
| **Tier** | **1** |

---

### 5. Government Digital Services Public Documentation

| Field | Value |
|-------|-------|
| **Source** | Absher, Qiwa, Najiz, national gov portal — **public help/docs only** |
| **Source URL** | https://www.my.gov.sa/ · https://qiwa.sa/ |
| **Country** | SA |
| **Language** | ar-SA |
| **Domain** | government_services |
| **License Class** | L2 |
| **Estimated Size** | 50–300 MB |
| **Collection Difficulty** | 50 / 100 |
| **Saudi Relevance** | 92 |
| **Arabic Relevance** | 90 |
| **Business Relevance** | 65 |
| **Technical Relevance** | 25 |
| **Strategic Value** | 90 |
| **Priority Score** | **84** |
| **Tier** | **1** |
| **Notes** | No authenticated scraping; public documentation pages only. |

---

### 6. ZATCA Tax & E-Invoicing Guidance

| Field | Value |
|-------|-------|
| **Source** | Zakat, Tax and Customs Authority |
| **Source URL** | https://zatca.gov.sa/ |
| **Country** | SA |
| **Language** | ar-SA |
| **Domain** | business / regulatory |
| **License Class** | L1 |
| **Estimated Size** | 40–200 MB |
| **Collection Difficulty** | 40 / 100 |
| **Saudi Relevance** | 88 |
| **Arabic Relevance** | 88 |
| **Business Relevance** | 92 |
| **Technical Relevance** | 35 |
| **Strategic Value** | 85 |
| **Priority Score** | **83** |
| **Tier** | **1** |

---

### 7. Monsha'at / Chambers SME & Entrepreneurship Content

| Field | Value |
|-------|-------|
| **Source** | Monsha'at, Saudi Chambers of Commerce public materials |
| **Source URL** | https://monshaat.gov.sa/ |
| **Country** | SA |
| **Language** | ar-SA |
| **Domain** | business / entrepreneurship |
| **License Class** | L2 |
| **Estimated Size** | 30–120 MB |
| **Collection Difficulty** | 48 / 100 |
| **Saudi Relevance** | 88 |
| **Arabic Relevance** | 85 |
| **Business Relevance** | 90 |
| **Technical Relevance** | 25 |
| **Strategic Value** | 80 |
| **Priority Score** | **80** |
| **Tier** | **1** |

---

### 8. Arabic Wikipedia (SA/GCC Filtered)

| Field | Value |
|-------|-------|
| **Source** | Wikimedia Arabic dump + category filters |
| **Source URL** | https://dumps.wikimedia.org/arwiki/ |
| **Country** | MULTI (SA/GCC-weighted) |
| **Language** | ar |
| **Domain** | academic / general |
| **License Class** | L2 (CC BY-SA) |
| **Estimated Size** | 400–800 MB filtered text |
| **Collection Difficulty** | 30 / 100 |
| **Saudi Relevance** | 70 |
| **Arabic Relevance** | 95 |
| **Business Relevance** | 50 |
| **Technical Relevance** | 25 |
| **Strategic Value** | 78 |
| **Priority Score** | **78** |
| **Tier** | **2** |
| **Notes** | Manifest: `wikipedia_ar.yaml`. Legal review for weight release (SA). |

---

### 9. Saudi Exchange (Tadawul) Public Disclosures

| Field | Value |
|-------|-------|
| **Source** | Saudi Exchange listed company disclosures |
| **Source URL** | https://www.saudiexchange.sa/ |
| **Country** | SA |
| **Language** | ar, en |
| **Domain** | business / finance |
| **License Class** | L2 |
| **Estimated Size** | 200 MB–2 GB |
| **Collection Difficulty** | 55 / 100 |
| **Saudi Relevance** | 85 |
| **Arabic Relevance** | 80 |
| **Business Relevance** | 90 |
| **Technical Relevance** | 40 |
| **Strategic Value** | 82 |
| **Priority Score** | **77** |
| **Tier** | **2** |

---

### 10. Etimad Government Procurement Public Docs

| Field | Value |
|-------|-------|
| **Source** | Etimad platform public procurement documentation |
| **Source URL** | https://portal.etimad.sa/ |
| **Country** | SA |
| **Language** | ar-SA |
| **Domain** | business / government |
| **License Class** | L2 |
| **Estimated Size** | 50–400 MB |
| **Collection Difficulty** | 52 / 100 |
| **Saudi Relevance** | 82 |
| **Arabic Relevance** | 85 |
| **Business Relevance** | 88 |
| **Technical Relevance** | 30 |
| **Strategic Value** | 78 |
| **Priority Score** | **77** |
| **Tier** | **2** |

---

### 11. MADAR Corpus (Gulf / Saudi Dialect Subset)

| Field | Value |
|-------|-------|
| **Source** | MADAR parallel dialect corpus |
| **Source URL** | https://camel.abudhabi.nyu.edu/madar/ |
| **Country** | GCC |
| **Language** | ar-Gulf, ar-SA |
| **Domain** | dialogue / dialect |
| **License Class** | L2 |
| **Estimated Size** | 5–50 MB (subset) |
| **Collection Difficulty** | 35 / 100 |
| **Saudi Relevance** | 75 |
| **Arabic Relevance** | 90 |
| **Business Relevance** | 30 |
| **Technical Relevance** | 20 |
| **Strategic Value** | 72 |
| **Priority Score** | **77** |
| **Tier** | **2** |

---

### 12. Partner-Licensed Business Correspondence

| Field | Value |
|-------|-------|
| **Source** | Partner DSA — formal Arabic business email, MOU excerpts, pitch decks |
| **Source URL** | Partner agreement (no public URL) |
| **Country** | SA |
| **Language** | ar-SA |
| **Domain** | business |
| **License Class** | L3 |
| **Estimated Size** | 10–500 MB (negotiated) |
| **Collection Difficulty** | 75 / 100 |
| **Saudi Relevance** | 85 |
| **Arabic Relevance** | 90 |
| **Business Relevance** | 95 |
| **Technical Relevance** | 20 |
| **Strategic Value** | 92 |
| **Priority Score** | **72** |
| **Tier** | **2** |
| **Notes** | High moat potential; legal review mandatory. |

---

### 13. GCC Economic & Trade Public Reports

| Field | Value |
|-------|-------|
| **Source** | GCC Secretariat, IMF, World Bank — GCC/Saudi sections |
| **Source URL** | https://www.gcc-sg.org/ · https://www.imf.org/ |
| **Country** | GCC |
| **Language** | ar, en |
| **Domain** | business / economics |
| **License Class** | L1 |
| **Estimated Size** | 100–500 MB |
| **Collection Difficulty** | 42 / 100 |
| **Saudi Relevance** | 60 |
| **Arabic Relevance** | 75 |
| **Business Relevance** | 85 |
| **Technical Relevance** | 25 |
| **Strategic Value** | 70 |
| **Priority Score** | **71** |
| **Tier** | **2** |

---

### 14. Open Academic Arabic Text

| Field | Value |
|-------|-------|
| **Source** | Open Arabic research corpora (e.g. ACL anthology AR, open thesis subsets) |
| **Source URL** | Various — per-source manifest |
| **Country** | MULTI |
| **Language** | ar |
| **Domain** | academic |
| **License Class** | L2 |
| **Estimated Size** | 200 MB–1 GB |
| **Collection Difficulty** | 45 / 100 |
| **Saudi Relevance** | 50 |
| **Arabic Relevance** | 90 |
| **Business Relevance** | 55 |
| **Technical Relevance** | 50 |
| **Strategic Value** | 65 |
| **Priority Score** | **68** |
| **Tier** | **2** |

---

### 15. UN Parallel Corpus (Arabic–English)

| Field | Value |
|-------|-------|
| **Source** | United Nations parallel documents |
| **Source URL** | https://www.uncorpora.org/ |
| **Country** | MULTI |
| **Language** | ar, en |
| **Domain** | translation / formal |
| **License Class** | L1 |
| **Estimated Size** | 100–300 MB |
| **Collection Difficulty** | 25 / 100 |
| **Saudi Relevance** | 40 |
| **Arabic Relevance** | 85 |
| **Business Relevance** | 55 |
| **Technical Relevance** | 30 |
| **Strategic Value** | 65 |
| **Priority Score** | **69** |
| **Tier** | **3** |

---

### 16. Licensed Regional Arabic News Archive

| Field | Value |
|-------|-------|
| **Source** | Licensed news publisher archive (KSA/GCC) |
| **Source URL** | Commercial license (TBD) |
| **Country** | SA / GCC |
| **Language** | ar |
| **Domain** | news |
| **License Class** | L3 |
| **Estimated Size** | 1–20 GB |
| **Collection Difficulty** | 80 / 100 |
| **Saudi Relevance** | 80 |
| **Arabic Relevance** | 88 |
| **Business Relevance** | 60 |
| **Technical Relevance** | 15 |
| **Strategic Value** | 75 |
| **Priority Score** | **67** |
| **Tier** | **3** |

---

### 17. OSCAR Arabic (Heavy Quality Filter)

| Field | Value |
|-------|-------|
| **Source** | OSCAR corpus Arabic subset |
| **Source URL** | https://huggingface.co/datasets/oscar |
| **Country** | MULTI |
| **Language** | ar |
| **Domain** | web |
| **License Class** | L1 (verify snapshot) |
| **Estimated Size** | 1–10 GB filtered |
| **Collection Difficulty** | 70 / 100 |
| **Saudi Relevance** | 45 |
| **Arabic Relevance** | 80 |
| **Business Relevance** | 40 |
| **Technical Relevance** | 20 |
| **Strategic Value** | 55 |
| **Priority Score** | **60** |
| **Tier** | **3** |
| **Notes** | High noise; use only after strong filters. |

---

### 18. Arabic Developer Q&A (Stack Overflow Mirrors)

| Field | Value |
|-------|-------|
| **Source** | Stack Overflow data dump — Arabic-tagged/filtered |
| **Source URL** | https://archive.org/details/stackexchange |
| **Country** | GLOBAL |
| **Language** | mixed-ar-en |
| **Domain** | code / dialogue |
| **License Class** | L2 (CC BY-SA) |
| **Estimated Size** | 50–300 MB filtered |
| **Collection Difficulty** | 45 / 100 |
| **Saudi Relevance** | 35 |
| **Arabic Relevance** | 70 |
| **Business Relevance** | 45 |
| **Technical Relevance** | 88 |
| **Strategic Value** | 68 |
| **Priority Score** | **59** |
| **Tier** | **3** |

---

### 19. The Stack / OSS Code (Arabic Signal Filter)

| Field | Value |
|-------|-------|
| **Source** | BigCode The Stack — Arabic comments/README filter |
| **Source URL** | https://huggingface.co/datasets/bigcode/the-stack |
| **Country** | GLOBAL |
| **Language** | mixed-ar-en |
| **Domain** | code |
| **License Class** | L1 (per-repo matrix) |
| **Estimated Size** | 1–10 GB filtered |
| **Collection Difficulty** | 60 / 100 |
| **Saudi Relevance** | 25 |
| **Arabic Relevance** | 45 |
| **Business Relevance** | 40 |
| **Technical Relevance** | 95 |
| **Strategic Value** | 70 |
| **Priority Score** | **51** |
| **Tier** | **3** |
| **Notes** | Manifest: `programming_corpus.yaml`. Phase D only. |

---

### 20. Common Crawl Arabic (Aggressive Filter)

| Field | Value |
|-------|-------|
| **Source** | Common Crawl — Arabic language filter |
| **Source URL** | https://commoncrawl.org/ |
| **Country** | MULTI |
| **Language** | ar |
| **Domain** | web |
| **License Class** | L1 (verify) |
| **Estimated Size** | 5–50 GB filtered |
| **Collection Difficulty** | 85 / 100 |
| **Saudi Relevance** | 30 |
| **Arabic Relevance** | 65 |
| **Business Relevance** | 30 |
| **Technical Relevance** | 20 |
| **Strategic Value** | 40 |
| **Priority Score** | **51** |
| **Tier** | **3** |
| **Notes** | Last resort volume; quality risk high. |

---

## Tier Definitions & Groupings

### Tier 1 — Must-Have (7 datasets)

Non-negotiable for Saudi-first differentiation. Collect and process **before** general Arabic web scale-up.

1. Vision 2030 Official Publications  
2. Saudi Open Data Portal (curated subsets)  
3. Saudi Ministry of Culture — Heritage & Public Content  
4. MISA Investment & Business Setup Guides  
5. Government Digital Services Public Documentation  
6. ZATCA Tax & E-Invoicing Guidance  
7. Monsha'at / Chambers SME & Entrepreneurship Content  

**Combined intent:** ≥ **40%** of initial Saudi-weighted training mix (ADR-004).

---

### Tier 2 — High Value (7 datasets)

Collect after Tier 1 manifests approved and Phase A success criteria met.

8. Arabic Wikipedia (SA/GCC filtered)  
9. Saudi Exchange (Tadawul) Public Disclosures  
10. Etimad Government Procurement Public Docs  
11. MADAR Corpus (Gulf subset)  
12. Partner-Licensed Business Correspondence  
13. GCC Economic & Trade Public Reports  
14. Open Academic Arabic Text  

---

### Tier 3 — Optional / Future (6 datasets)

Phase E or later; volume or license complexity; never dilute Tier 1 signal.

15. UN Parallel Corpus  
16. Licensed Regional Arabic News Archive  
17. OSCAR Arabic  
18. Arabic Developer Q&A  
19. The Stack / OSS Code  
20. Common Crawl Arabic  

---

## Weighted Acquisition Framework

### Component scores (all 0–100)

| Component | Symbol | Description |
|-----------|--------|-------------|
| Saudi relevance | `S` | KSA specificity: gov, policy, business, culture |
| Arabic relevance | `A` | MSA quality, dialect coverage, Arabic reasoning value |
| License safety | `L` | Derived from license class (see below) |
| Collection ease | `E` | `100 − Collection Difficulty` |
| Strategic value | `V` | Long-term moat, benchmark lift, competitor gap |

**License safety mapping (`L`):**

| Class | L score |
|-------|---------|
| L0 | 100 |
| L1 | 90 |
| L2 | 75 |
| L3 | 40 |
| L4 | 0 (do not acquire) |

### Priority formula

```
Priority = 0.30×S + 0.25×A + 0.20×V + 0.15×L + 0.10×E
```

**Rationale:**

| Weight | Why |
|--------|-----|
| 30% Saudi | Saudi-first is the primary wedge |
| 25% Arabic | Arabic-first quality — not just KSA English docs |
| 20% Strategic | Long-term moat beats one-off volume |
| 15% License | Safer data = shippable model |
| 10% Ease | Tie-breaker — prefer faster legal wins early |

**Optional gate:** If `L < 50` (L3+), **cap Priority at 75** until legal approval recorded.

**Business / technical relevance** inform `V` and tier placement but are not separate formula terms — they feed strategic value scoring during quarterly review.

---

## Collection Roadmap

### Phase A — Government & Public Saudi Knowledge

| | |
|--|--|
| **Goals** | Ingest Tier 1 gov/policy sources; manifests approved; legal snapshots filed |
| **Datasets** | #1 Vision 2030, #2 Open Data, #3 Culture, #5 Gov digital services |
| **Risks** | PDF extraction quality; per-dataset license variance; stale policy text |
| **Expected impact** | +10–15 pts Saudi knowledge benchmark (post fine-tune estimate) |
| **Success criteria** | ≥ 4 Tier-1 manifests `status: collected`; ≥ 100K clean Saudi gov tokens; legal review 100% for L2+ |

---

### Phase B — Arabic Knowledge

| | |
|--|--|
| **Goals** | Broad Arabic fluency without diluting Saudi signal |
| **Datasets** | #8 Wikipedia AR filtered, #11 MADAR Gulf, #14 Academic Arabic |
| **Risks** | CC BY-SA weight release; dialect/MSA mix confusion |
| **Expected impact** | +5–8 pts Arabic reasoning; improved register control |
| **Success criteria** | Arabic quality score ≥ 0.65 on processed shards; Saudi mix still ≥ 40% weighted |

---

### Phase C — Business Knowledge

| | |
|--|--|
| **Goals** | Business-aware differentiation — formal Arabic, compliance, investment |
| **Datasets** | #4 MISA, #6 ZATCA, #7 Monsha'at, #9 Tadawul, #10 Etimad, #12 Partner correspondence, #13 GCC reports |
| **Risks** | L3 partner delays; financial data accuracy; hallucination on regulations |
| **Expected impact** | +8–12 pts business benchmark; enterprise pilot readiness |
| **Success criteria** | ≥ 6 business manifests collected; business benchmark ≥ 72 internal floor |

---

### Phase D — Programming Knowledge

| | |
|--|--|
| **Goals** | Preserve code capability; Arabic problem statements |
| **Datasets** | #19 The Stack filtered, #18 Arabic Dev Q&A |
| **Risks** | License matrix complexity; secrets in code; regression if over-weighted |
| **Expected impact** | Maintain ≥ 95% Phase 4 programming baseline |
| **Success criteria** | Programming score ≥ 90; secrets scan zero critical; mix cap ≤ 10% code tokens |

---

### Phase E — Specialized Corpora

| | |
|--|--|
| **Goals** | Optional scale and translation — only if Tier 1–D gates met |
| **Datasets** | #15 UN, #16 News archive, #17 OSCAR, #20 Common Crawl |
| **Risks** | Quality collapse; copyright; poisoning via web crawl |
| **Expected impact** | Volume and translation lift — marginal if Tier 1 strong |
| **Success criteria** | No regression on Saudi/Arabic gates; quality score ≥ 0.65 on new shards only |

---

## Manifest & Governance Integration

Every acquisition target requires:

1. YAML manifest in `data/datasets/manifests/`  
2. License class and `legal_risk` per [LICENSING_GUIDE.md](LICENSING_GUIDE.md)  
3. Priority score recorded in manifest `notes`  
4. PR review by `@TBD-data-team` (CODEOWNERS)  
5. No bytes in git — external snapshot ref only  

---

## Related Documents

- [DATA_MOAT_STRATEGY.md](DATA_MOAT_STRATEGY.md)
- [DATA_RISKS.md](DATA_RISKS.md)
- [DATA_TARGETS.md](DATA_TARGETS.md)
- [DATA_STRATEGY.md](DATA_STRATEGY.md)
- [DECISIONS.md](DECISIONS.md) — ADR-004
