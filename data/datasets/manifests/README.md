# Dataset Manifests

This directory is the **authoritative registry** of every dataset proposed, reviewed, or approved for ArabArenaAI-1. Manifests are version-controlled YAML files. **Raw and processed dataset bytes are never stored in git** — only metadata, provenance, and governance status.

---

## Purpose of Manifests

Manifests exist to:

1. **Register intent** — document what we plan to collect before any bytes are ingested
2. **Enforce licensing** — every source must have a license class (L0–L4) before collection
3. **Enable audit trails** — reviewers, dates, legal risk, and quality scores are traceable
4. **Support reproducibility** — training runs reference manifest IDs and snapshot refs, not mystery folders
5. **Protect the project** — block unlicensed, high-risk, or low-quality sources at the gate

See also: [docs/DATASET_MANIFEST_TEMPLATE.md](../../docs/DATASET_MANIFEST_TEMPLATE.md) · [docs/LICENSING_GUIDE.md](../../docs/LICENSING_GUIDE.md) · [docs/DATA_STRATEGY.md](../../docs/DATA_STRATEGY.md)

---

## Dataset Registration Process

```
┌─────────────┐    ┌──────────────┐    ┌───────────────┐    ┌────────────┐
│  Identify   │───►│  Create YAML │───►│ Legal review  │───►│  Approved  │
│  source     │    │  manifest    │    │  (L2–L4 req.) │    │  for collect│
└─────────────┘    └──────────────┘    └───────────────┘    └────────────┘
                          │                    │
                          ▼                    ▼
                   status: proposed      status: rejected
```

### Step-by-step

| Step | Action | Owner |
|------|--------|-------|
| 1 | Identify source URL, domain, and Saudi/GCC relevance | Data team |
| 2 | Copy fields from [DATASET_MANIFEST_TEMPLATE.md](../../docs/DATASET_MANIFEST_TEMPLATE.md) into a new `{slug}.yaml` | Contributor |
| 3 | Set `status: proposed` and assign `license` class (L0–L4) | Contributor |
| 4 | Open PR with manifest only — **no dataset files** | Contributor |
| 5 | Legal review for L2+; data lead review for all | Legal / Data lead |
| 6 | On approval: set `status: approved`, `approved_by`, `approved_date` | Reviewer |
| 7 | Collection (Phase 2+) writes snapshot to external storage; update `source_snapshot_ref` | Data ops |
| 8 | Phase 3 cleaning updates `quality_score`; Phase 5 training references manifest ID | ML pipeline |

### Manifest status values

| Status | Meaning |
|--------|---------|
| `proposed` | Cataloged; not yet approved for collection |
| `approved` | Cleared for collection and downstream use |
| `collected` | Raw snapshot stored externally; ref recorded |
| `processed` | Cleaning complete; quality score assigned |
| `rejected` | Do not collect or train |
| `deprecated` | Superseded or license expired |

---

## Licensing Requirements

**No collection without a recorded license class.**

| Class | Summary | Collection allowed? |
|-------|---------|---------------------|
| **L0** | Public domain | Yes, after data lead review |
| **L1** | Open commercial | Yes, after data lead review |
| **L2** | Attribution required | Yes, with attribution plan documented |
| **L3** | Restricted — legal review required | Only after written legal approval |
| **L4** | Forbidden | **Never** |

Full definitions: [docs/LICENSING_GUIDE.md](../../docs/LICENSING_GUIDE.md)

### Required for every manifest

- `license` — class + license name (e.g. `L1 — CC-BY-4.0`)
- `legal_risk` — `low` · `medium` · `high`
- `source_url` — canonical link to terms or dataset page
- Notes on **training_allowed** and **redistribution_allowed** (when known)

License text snapshots (PDF/HTML) belong in `docs/legal/licenses/` — not in this directory.

---

## Quality Review Workflow

Quality scoring happens in **Phase 3 (cleaning)**. At manifest time, use **estimated** quality and document known risks.

### Phase 2 (manifest / catalog)

- [ ] Source relevance to Saudi-first / Arabic-first priorities documented in `notes`
- [ ] License class assigned; L3+ has legal ticket reference
- [ ] `expected_size` and `collection_method` realistic
- [ ] `legal_risk` assessed honestly
- [ ] No duplicate `dataset_name`

### Phase 3 (post-cleaning)

- [ ] `quality_score` updated (0.0–1.0) per [DATA_STRATEGY.md](../../docs/DATA_STRATEGY.md)
- [ ] PII audit sample completed
- [ ] Deduplication against existing corpus documented
- [ ] Reject if score **< 0.50**; human review if **0.50–0.64**

### Quality score bands

| Score | Action |
|-------|--------|
| 0.80–1.00 | Premium — prioritize in Saudi/Arabic mix |
| 0.65–0.79 | Standard inclusion |
| 0.50–0.64 | Marginal — requires human review |
| < 0.50 | Reject — do not train |

---

## Example Manifests (this directory)

| File | Description | Status |
|------|-------------|--------|
| [saudi_open_data.yaml](saudi_open_data.yaml) | Saudi Open Data Portal — government datasets | `proposed` |
| [vision2030.yaml](vision2030.yaml) | Vision 2030 official publications | `proposed` |
| [wikipedia_ar.yaml](wikipedia_ar.yaml) | Arabic Wikipedia (MSA encyclopedic) | `proposed` |
| [programming_corpus.yaml](programming_corpus.yaml) | Open code corpus with Arabic technical text | `proposed` |

> These are **inventory placeholders**. No data has been downloaded. URLs and sizes are planning estimates.

---

## Related Documents

- [docs/DATA_PIPELINE.md](../../docs/DATA_PIPELINE.md) — end-to-end data flow
- [docs/DECISIONS.md](../../docs/DECISIONS.md) — ADR-004 Saudi-first knowledge strategy
- [docs/DATA_STRATEGY.md](../../docs/DATA_STRATEGY.md) — corpus mix and cleaning standards
