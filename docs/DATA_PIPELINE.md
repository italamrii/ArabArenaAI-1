# Data Pipeline — ArabArenaAI-1

This document describes the **planned end-to-end data flow** from source identification through training-ready shards. **No pipeline code exists yet** — this is the operational blueprint for Phases 2–5.

Related: [DATA_STRATEGY.md](DATA_STRATEGY.md) · [LICENSING_GUIDE.md](LICENSING_GUIDE.md) · [../data/datasets/manifests/README.md](../data/datasets/manifests/README.md)

---

## Pipeline Overview

```
┌────────┐   ┌──────────┐   ┌──────────────┐   ┌────────────┐
│ Source │──►│ Manifest │──►│ Legal Review │──►│ Collection │
└────────┘   └──────────┘   └──────────────┘   └────────────┘
                                                      │
     ┌────────────────────────────────────────────────┘
     ▼
┌──────────┐   ┌───────────────┐   ┌─────────────┐   ┌───────────┐
│ Cleaning │──►│ Deduplication │──►│ Evaluation  │──►│ Training  │
└──────────┘   └───────────────┘   └─────────────┘   └───────────┘
```

Each stage has **entry criteria**, **artifacts**, and **exit gates**. A stage must not start until the prior gate passes.

---

## Stage 1 — Source

**Goal:** Identify candidate data sources aligned with [ADR-004 Saudi-first knowledge strategy](DECISIONS.md).

| Input | Output |
|-------|--------|
| Research, partner offers, open data catalogs | Source candidate brief |

**Activities:**

- Map source to priority domain (Saudi > GCC > Arabic > Business > Engineering > Global)
- Record canonical `source_url` and estimated relevance
- Flag obvious L4 sources (ToS prohibits ML training, authenticated-only, unknown license)

**Exit gate:** Candidate documented; ready for manifest PR.

**Artifact location:** Issue or PR description → becomes manifest YAML.

---

## Stage 2 — Manifest

**Goal:** Register the dataset in version control **before** any bytes are collected.

| Input | Output |
|-------|--------|
| Source candidate | `{dataset_name}.yaml` in `data/datasets/manifests/` |

**Required fields:** See [DATASET_MANIFEST_TEMPLATE.md](DATASET_MANIFEST_TEMPLATE.md) and example manifests.

**Activities:**

- Assign `license_class` (L0–L4) and `legal_risk`
- Set `status: proposed`
- Document `collection_method` and `expected_size`
- Open PR — manifest only, no data files

**Exit gate:** Data lead acknowledges manifest completeness.

---

## Stage 3 — Legal Review

**Goal:** Confirm training and redistribution rights before collection.

| Input | Output |
|-------|--------|
| Proposed manifest | Approved / rejected / conditional approval |

**Review matrix:**

| Class | Reviewer | SLA (target) |
|-------|----------|--------------|
| L0, L1 | Data lead | 2 business days |
| L2 | Data lead + attribution plan | 3 business days |
| L3 | Legal counsel | 10 business days |
| L4 | Auto-reject | Immediate |

**Activities:**

- Snapshot license text to `docs/legal/licenses/{dataset_name}/`
- Record `training_allowed`, `redistribution_allowed`
- Set `approved_by`, `approved_date`, `status: approved` or `rejected`

**Exit gate:** `status: approved` for collection; L4 never proceeds.

---

## Stage 4 — Collection

**Goal:** Ingest raw data into **external storage** — not git.

| Input | Output |
|-------|--------|
| Approved manifest | Immutable raw snapshot |

**Storage targets (per ADR-002):**

- Cloudflare R2 / S3 — raw blobs
- Hugging Face Datasets — publishable subsets only (post-legal)
- Internal vault — L3 restricted sources

**Activities:**

- Execute `collection_method` from manifest
- Write snapshot with content hash and timestamp
- Update manifest: `status: collected`, `source_snapshot_ref`, `collection_date`
- Log record counts vs `expected_size`

**Exit gate:** Snapshot hash recorded; manifest updated; no PII surprises on spot check.

**Artifact location:** `data/datasets/raw/` (local cache, gitignored) + external URI in manifest.

---

## Stage 5 — Cleaning

**Goal:** Normalize, filter, and quality-score text for training.

| Input | Output |
|-------|--------|
| Raw snapshot | Processed shards |

**Activities (Phase 3 implementation):**

- Unicode NFC normalization; Arabic diacritics policy
- Language ID; length filters; toxicity/PII filters
- Layout extraction for PDFs (Vision 2030, open data reports)
- Assign `quality_score` (0.0–1.0) per [DATA_STRATEGY.md](DATA_STRATEGY.md)
- Reject shards below 0.50; quarantine 0.50–0.64 for human review

**Exit gate:** Mean quality ≥ 0.65 on approved mix; PII audit passed.

**Artifact location:** `data/datasets/processed/` (gitignored) + external URI in manifest.

---

## Stage 6 — Deduplication

**Goal:** Remove exact and near-duplicate content across sources and splits.

**Activities:**

- Exact hash dedupe on normalized text
- MinHash / SimHash near-duplicate at paragraph and document level
- Cross-source dedupe before train/val/test split
- **Benchmark holdout ban** — remove any item matching evaluation benchmark hashes

**Exit gate:** Duplication rate documented; zero leakage on holdout check.

---

## Stage 7 — Evaluation (data quality)

**Goal:** Validate processed data **before** it enters training — distinct from model benchmark eval (Phase 4+).

**Checks:**

| Check | Threshold |
|-------|-----------|
| Language purity (Arabic corpora) | ≥ 95% Arabic in AR-tagged shards |
| Saudi-tagged subset presence | Meets ADR-004 mix targets |
| Toxicity sample | Below agreed rate |
| Secret/PII scan | Zero critical findings |
| Manifest completeness | 100% of shards traceable to manifest ID |

**Exit gate:** Data quality report signed by data lead; manifests set `status: processed`.

**Artifact location:** Report in external storage; summary in PR for mix changes.

---

## Stage 8 — Training

**Goal:** Consume processed shards in fine-tuning (Phase 5) with full reproducibility.

**Activities:**

- Build training mix from manifests with `status: processed` and `quality_score ≥ 0.65`
- Log manifest IDs, snapshot hashes, and mix weights in experiment config
- Enforce ADR-004 Saudi-first mix ratios
- Never train on benchmark holdout data

**Exit gate:** Experiment config references immutable data snapshot IDs; ML lead sign-off.

**Artifact location:** `training/configs/` + `training/experiments/` (gitignored outputs).

---

## Stage Summary Table

| Stage | Phase | Owner | Key artifact |
|-------|-------|-------|--------------|
| Source | 2 | Data team | Candidate brief |
| Manifest | 2 | Contributor | `manifests/*.yaml` |
| Legal review | 2 | Legal / Data lead | License snapshot |
| Collection | 2–3 | Data ops | Raw snapshot (external) |
| Cleaning | 3 | Data eng | Processed shards |
| Deduplication | 3 | Data eng | Dedupe report |
| Evaluation | 3 | Data + Eval | Data QA report |
| Training | 5 | ML team | Experiment config |

---

## Observability & Audit

Every shard should be traceable:

```
manifest_id → raw snapshot hash → processed shard hash → experiment_id
```

Future `scripts/` utilities (Phase 3) will validate this chain. Until then, manual checklists in PRs are required.

---

## Related Documents

- [DATA_STRATEGY.md](DATA_STRATEGY.md)
- [LICENSING_GUIDE.md](LICENSING_GUIDE.md)
- [DATASET_MANIFEST_TEMPLATE.md](DATASET_MANIFEST_TEMPLATE.md)
- [DECISIONS.md](DECISIONS.md) — ADR-002, ADR-004
- [METRICS.md](METRICS.md) — training regression KPIs
