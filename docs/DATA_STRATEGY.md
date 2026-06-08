# Data Strategy — ArabArenaAI-1

This document defines how ArabArenaAI-1 collects, licenses, cleans, and governs training and evaluation data. Data is the primary moat for a **Saudi-first, Arabic-first** model — strategy must precede scale.

---

## Objectives

1. **Priority-weighted corpus** — Saudi > GCC > Arabic > Business > Engineering > Global
2. **License clarity** — no source enters the pipeline without recorded rights
3. **Quality over volume** — gated ingestion with measurable quality scores
4. **Auditability** — full provenance from raw source to training shard
5. **Safety** — PII redaction, sensitive content filtering, partner data isolation

---

## Data Directory Layout

```
data/datasets/
├── raw/           # Immutable ingested sources (local or object storage; gitignored)
└── processed/     # Cleaned, deduplicated, split shards (gitignored)
```

Manifests, schemas, and license metadata **are** version-controlled; raw bytes are not.

---

## Saudi Datasets (Priority 1)

### Target Content Types

| Category | Examples | Use |
|----------|----------|-----|
| Government & policy | Vision 2030 docs, ministry publications, open data portals | Saudi knowledge, formal Arabic |
| Business & economy | Tadawul disclosures (licensed), SME guides, chamber content | Business terminology |
| Culture & society | Licensed news, heritage content, regional etiquette guides | Cultural fluency |
| Dialect | Transcripts, conversational datasets (with consent/license) | Saudi/Khaleeji dialect |
| Services | Government service descriptions (Absher, Qiwa, etc. — public docs only) | Practical assistance |

### Collection Principles

- Prefer **official open data** and **explicitly licensed** archives
- Document **jurisdiction** (KSA vs broader GCC) per record
- Flag **time sensitivity** (policies change; include source date)
- Never scrape authenticated portals or bypass terms of service

### Known Sources (to evaluate in Phase 2)

- Saudi Open Data Portal (data.gov.sa)
- Vision 2030 official publications
- Arabic Wikipedia (SA-relevant articles subset)
- Licensed regional news archives (legal review required)
- Partner-contributed corpora under data sharing agreements

---

## Arabic Datasets (Priority 3 — after Saudi/GCC weighting)

### Target Content Types

- Modern Standard Arabic (MSA) news, books, academic text
- Gulf Arabic where dialect coverage is required
- Bilingual Arabic–English technical and business text
- Arabic instruction-following examples (human-written preferred)

### Public Arabic Corpora (candidates)

| Source | License (verify at ingest) | Notes |
|--------|---------------------------|-------|
| OSCAR (Arabic subset) | Verify per snapshot | Web crawl; high noise |
| Arabic Wikipedia | CC BY-SA | Strong MSA; filter for quality |
| MADAR / dialect resources | Per dataset | Dialect coverage |
| UN parallel corpora | Per dataset | Translation pairs |
| Common Crawl (AR filter) | CC0 / restricted | Requires aggressive cleaning |

**Rule:** License terms must be verified at ingest time — not assumed from this table.

---

## Public & Open-Source Datasets (Priority 6 — Global Knowledge)

Used sparingly and **after** regional corpora to avoid diluting Saudi/GCC signal:

- The Stack / code corpora (programming capability)
- Open instruction datasets (filter for Arabic relevance or translate-with-audit)
- Math/reasoning sets (evaluate Arabic adaptation need)

Global data must not exceed agreed mix ratios without explicit approval (target mix TBD in Phase 2 manifest).

---

## Data Licensing Framework

### License Classes

| Class | Description | Training | Redistribution |
|-------|-------------|----------|----------------|
| **L0 — Public domain / permissive OSS** | Apache, MIT, CC0 | Allowed | Allowed with attribution |
| **L1 — CC BY / BY-SA** | Attribution required | Allowed | Check SA obligations |
| **L2 — Research-only** | Academic/non-commercial | Internal R&D only | No public weight release |
| **L3 — Commercial licensed** | Paid or partner agreement | Per contract | Per contract |
| **L4 — Prohibited** | Unknown or restrictive ToS | **Blocked** | **Blocked** |

### Required Metadata (per dataset row)

```yaml
dataset_id: unique-slug
source_name: human-readable name
source_url: canonical URL or partner reference
license_class: L0-L4
license_text_ref: path to license snapshot
jurisdiction: SA | GCC | AR | GLOBAL
language: ar | ar-SA | ar-Gulf | en | mixed
content_type: news | gov | business | code | dialogue | ...
collection_date: ISO-8601
retention_policy: permanent | expire-on-date
pii_status: none | redacted | unknown
quality_score: 0.0-1.0 (post-cleaning)
approved_by: reviewer id
```

---

## Dataset Quality Rules

### Inclusion Criteria

- License class L0–L3 with written approval for L3
- UTF-8 valid Arabic text (or documented mixed script)
- Minimum length thresholds per content type
- Source date recorded for time-sensitive facts
- Duplicate check against existing corpus

### Exclusion Criteria

- Unknown license or ToS violation risk
- Heavy spam, SEO farms, or machine-translated garbage
- Unredacted PII (names, IDs, phone numbers, addresses)
- Hate, harassment, or illegal content
- English-only content (unless explicitly for translation/code tasks)

### Quality Scoring Dimensions (0–1 each)

| Dimension | Weight | Description |
|-----------|--------|-------------|
| Fluency | 0.25 | Grammatical, natural Arabic |
| Relevance | 0.30 | Saudi/GCC/business/engineering alignment |
| Factuality proxy | 0.20 | Consistency with trusted sources (sample audit) |
| Toxicity | 0.15 | Low harmful content (inverse score) |
| Uniqueness | 0.10 | Not near-duplicate of existing corpus |

**Minimum shard average:** 0.65 (calibrated in Phase 3 pilot)

---

## Data Cleaning Standards

### Normalization

- Unicode NFC normalization for Arabic
- Consistent handling of diacritics (policy: strip for general corpus unless diacritics task)
- Normalize Arabic-Indic vs Western numerals (document policy per corpus)
- Preserve code blocks and URLs in technical content
- RTL-safe storage; no broken bidirectional text

### Deduplication

1. **Exact** — SHA-256 on normalized text
2. **Near-duplicate** — MinHash / SimHash at document and paragraph level
3. **Cross-source** — dedupe across raw sources before mixing

### Filtering Pipeline (ordered)

1. Encoding and language ID (fastText or equivalent)
2. Length and structure filters
3. PII detection and redaction
4. Toxicity / NSFW classifier (human review queue for borderline)
5. Quality model or heuristic score
6. Manual audit sample (≥ 1% per new source)

### Splits

- **Train / validation / test** — stratified by source and content type
- **Leakage checks** — near-duplicate ban across splits
- **Holdout benchmark set** — frozen; never seen in training (stored separately under evaluation)

---

## Annotation Strategy

### When Human Annotation Is Required

- Instruction-following examples for Saudi-specific tasks
- Gold answers for benchmark items
- Preference pairs for RLHF/DPO (Phase 5+ if adopted)
- Dialect labeling (MSA vs Najdi vs Hijazi vs Gulf)
- Business formality register (legal, marketing, internal memo)

### Annotator Guidelines

- Native Arabic speakers with Saudi/GCC familiarity for regional tasks
- Dual review for Saudi knowledge gold labels
- Document inter-annotator agreement (IAA) target ≥ 0.80 Cohen's kappa on factual items
- No annotator PII in exported labels

### Synthetic Data Policy (future)

- Synthetic data allowed only with **disclosure**, **filtering**, and **mix ratio caps**
- No synthetic Saudi government facts without verification pipeline
- Prefer human-written regional content for high-stakes categories

---

## Storage & Security

- Raw and processed blobs in object storage (S3-compatible or regional cloud)
- Encryption at rest and in transit
- Partner data in isolated buckets with separate access IAM
- No dataset commits to git (see `.gitignore`)

---

## Phase 2 Deliverables Checklist

- [ ] Dataset inventory spreadsheet / manifest schema implemented
- [ ] Legal review workflow for L2/L3 sources
- [ ] First 10 Saudi-priority sources documented with license snapshots
- [ ] Cleaning spec signed off (this document → operational runbook)
- [ ] Annotation vendor or internal team charter (if applicable)

---

## Related Documents

- [MODEL_STRATEGY.md](MODEL_STRATEGY.md) — base model and training constraints
- [BENCHMARKS.md](BENCHMARKS.md) — evaluation data must not leak into training
- [../ROADMAP.md](../ROADMAP.md) — Phases 2–3 timeline
