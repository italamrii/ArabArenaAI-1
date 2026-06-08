# Dataset Manifest Template

Every dataset considered for ArabArenaAI-1 **must** have a manifest entry before ingest. Manifests are version-controlled; raw dataset bytes live in external storage only.

See [DATA_STRATEGY.md](DATA_STRATEGY.md) for license classes, quality rules, and cleaning standards.

---

## Required Fields

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| **Dataset name** | string | Unique slug (lowercase, hyphens) | `sa-vision2030-publications` |
| **Source** | string | Canonical URL, partner ID, or archive path | `https://vision2030.gov.sa/...` |
| **License** | string | License name + class (L0–L4) | `L0 — Saudi Open Data Terms` |
| **Country** | string | Primary country of origin | `SA` · `GCC` · `MULTI` |
| **Language** | string | ISO-style language tag(s) | `ar` · `ar-SA` · `mixed-ar-en` |
| **Domain** | string | Content domain | `government` · `business` · `news` · `code` · `dialogue` |
| **Collection date** | date | Date ingested or snapshot taken (ISO-8601) | `2026-06-08` |
| **Quality score** | float | 0.0–1.0 after cleaning pipeline (null until Phase 3) | `0.72` |
| **Notes** | string | Provenance, restrictions, known biases, PII status | See below |

---

## Optional Fields (recommended)

| Field | Description |
|-------|-------------|
| `manifest_id` | UUID for immutable reference |
| `source_snapshot_ref` | S3/R2/HF path to raw snapshot |
| `processed_ref` | Path to processed shard(s) |
| `record_count` | Approximate document or row count |
| `size_bytes` | Uncompressed size |
| `jurisdiction` | Legal jurisdiction for compliance |
| `pii_status` | `none` · `redacted` · `unknown` |
| `valid_until` | Expiry for time-sensitive licenses |
| `approved_by` | Reviewer ID |
| `approved_date` | ISO-8601 approval date |
| `training_allowed` | `yes` · `no` · `internal_only` |
| `redistribution_allowed` | `yes` · `no` · `conditional` |

---

## YAML Template

Copy for each dataset under `data/datasets/manifests/` (directory to be created in Phase 2):

```yaml
# Dataset manifest — ArabArenaAI-1
manifest_version: "1.0"

dataset_name: example-dataset-slug
source: "https://example.com/dataset-or-partner-ref"
license: "L0 — Apache-2.0"
license_text_ref: "docs/legal/licenses/example-apache-2.0.txt"  # snapshot path

country: SA          # SA | AE | GCC | MULTI | GLOBAL
language: ar-SA      # ar | ar-SA | ar-Gulf | en | mixed-ar-en
domain: business     # government | business | news | code | dialogue | academic | other

collection_date: 2026-06-08
quality_score: null  # 0.0–1.0 after Phase 3 cleaning; null at catalog time

notes: |
  Brief description of contents, relevance to Saudi-first strategy,
  known limitations, PII handling, and why this source was selected.

# --- Optional ---
# manifest_id: "550e8400-e29b-41d4-a716-446655440000"
# record_count: 125000
# size_bytes: 4500000000
# pii_status: none
# training_allowed: yes
# redistribution_allowed: conditional
# approved_by: reviewer-id
# approved_date: 2026-06-08
```

---

## CSV Template (bulk inventory)

For spreadsheet-based Phase 2 cataloging:

```csv
dataset_name,source,license,country,language,domain,collection_date,quality_score,notes
sa-open-data-example,https://data.gov.sa/...,L0 — Open Data,SA,ar,government,2026-06-08,,"Vision 2030 adjacent open dataset"
```

> **Note:** CSV manifests are for inventory only. Each approved dataset should also have a YAML record before training use. Large CSV exports belong in external storage — not committed if they contain sample text rows.

---

## Quality Score Guidance

Assigned in **Phase 3** after cleaning (see [DATA_STRATEGY.md](DATA_STRATEGY.md)):

| Score | Meaning |
|-------|---------|
| 0.0–0.49 | Reject — do not include in training mix |
| 0.50–0.64 | Marginal — human review required |
| 0.65–0.79 | Accept — standard inclusion |
| 0.80–1.00 | Premium — prioritize in Saudi/Arabic mix |

---

## Review Checklist (before `approved`)

- [ ] License class assigned (L0–L4) and legal review complete for L2+
- [ ] Country and language tags accurate
- [ ] Source URL or partner agreement on file
- [ ] PII status documented
- [ ] No duplicate `dataset_name` in inventory
- [ ] Training and redistribution flags set explicitly
- [ ] Notes explain Saudi/GCC relevance

---

## Related Documents

- [DATA_STRATEGY.md](DATA_STRATEGY.md)
- [DECISIONS.md](DECISIONS.md) — ADR-002 external storage policy
- [METRICS.md](METRICS.md) — quality impacts benchmark outcomes
