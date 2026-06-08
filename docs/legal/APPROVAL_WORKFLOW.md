# Approval Workflow — ArabArenaAI-1 Legal & Data Gates

Defines the **status lifecycle** from dataset proposal through training authorization. Legal review files in `docs/legal/licenses/` are the system of record alongside manifests in `data/datasets/manifests/`.

**No stage may be skipped.** Collection is **blocked** until **Collection Allowed** is explicitly recorded.

Related: [README.md](README.md) · [LICENSING_GUIDE.md](../LICENSING_GUIDE.md) · [DATA_PIPELINE.md](../DATA_PIPELINE.md)

---

## Status Lifecycle (Happy Path)

```
┌───────────┐   ┌──────────────┐   ┌──────────┐   ┌───────────────────┐
│ PROPOSED  │──►│ LEGAL REVIEW │──►│ APPROVED │──►│ COLLECTION ALLOWED│
└───────────┘   └──────────────┘   └──────────┘   └─────────┬─────────┘
                                                              │
                    ┌─────────────────────────────────────────┘
                    ▼
         ┌────────────────────┐   ┌──────────────────┐
         │ PROCESSING ALLOWED │──►│ TRAINING ALLOWED │
         └────────────────────┘   └──────────────────┘
```

---

## Status Definitions

### 1. Proposed

| | |
|--|--|
| **Meaning** | Dataset cataloged; manifest PR opened; no bytes collected |
| **Manifest** | `status: proposed` |
| **Legal file** | Review worksheet created from [template](licenses/template-license-review.md); `Final status: PENDING REVIEW` |
| **Who acts** | Data team |
| **Exit criteria** | Complete manifest fields; review file linked; PR ready for legal |

**Blocked:** Collection · Processing · Training

---

### 2. Legal Review

| | |
|--|--|
| **Meaning** | Legal counsel actively verifying terms and use permissions |
| **Manifest** | Remains `proposed` or `legal_review` (optional tag in `notes`) |
| **Legal file** | `Final status: PENDING REVIEW`; follow-up checklist in progress |
| **Who acts** | Legal counsel (lead); data team supports URLs and scope |
| **Exit criteria** | All permission fields verified or explicitly marked; risk class assigned; L0–L4 confirmed |

**Blocked:** Collection · Processing · Training

**SLA targets:** L1 Tier 1: 10 business days · L2: 15 · L3: 30 (see [README.md](README.md))

---

### 3. Approved

| | |
|--|--|
| **Meaning** | Legal counsel confirms use within stated scope |
| **Manifest** | `status: approved`; `approved_by`, `approved_date`; confirmed `license` class |
| **Legal file** | `Final status: APPROVED` or `APPROVED WITH CONDITIONS` |
| **Who acts** | Legal counsel signs; data lead updates manifest |
| **Exit criteria** | Approval block complete; conditions copied to manifest if any |

**Blocked:** Processing · Training (until collection completes)  
**Permitted:** **Collection** may begin → advance to Collection Allowed

---

### 4. Collection Allowed

| | |
|--|--|
| **Meaning** | Explicit authorization to fetch raw snapshots to external storage |
| **Manifest** | `status: collected` after snapshot; `source_snapshot_ref`, `collection_date` |
| **Legal file** | Workflow gate **Collection Allowed: ✅** |
| **Who acts** | Data ops per `collection_method` in manifest |
| **Exit criteria** | Snapshot hash logged; spot-check for PII; size within expected bounds |

**Blocked:** Training  
**Permitted:** Raw ingest only — no training mix

**Hard rule:** Manual gate checkbox in review file before first byte collected.

---

### 5. Processing Allowed

| | |
|--|--|
| **Meaning** | Cleaned shards may be produced from **approved** raw snapshot |
| **Manifest** | `quality_score` assigned; `status: processed` when done |
| **Legal file** | Workflow gate **Processing Allowed: ✅** (default: auto after successful collection audit unless conditions say otherwise) |
| **Who acts** | Data engineering (Phase 3 pipeline — future) |
| **Exit criteria** | Quality ≥ 0.65 mean; PII scan pass; dedupe report |

**Blocked:** Training until Training Allowed  
**Permitted:** Cleaning · deduplication · quality scoring

---

### 6. Training Allowed

| | |
|--|--|
| **Meaning** | Processed shards may enter fine-tuning mix (Phase 5+) |
| **Manifest** | Referenced in experiment config by manifest ID / hash |
| **Legal file** | Workflow gate **Training Allowed: ✅** |
| **Who acts** | ML lead after data + legal confirm no new conditions violated |
| **Exit criteria** | Experiment logs manifest IDs; mix respects ADR-004 and DATA_TARGETS |

**Permitted:** LoRA / fine-tune experiments per [MODEL_RELEASE_POLICY.md](../MODEL_RELEASE_POLICY.md)

**Note:** **Public weight release** is a **separate** legal gate — Training Allowed ≠ Public Release Allowed.

---

## Rejection Workflow

```
PROPOSED or LEGAL REVIEW
         │
         ▼ (terms prohibit use / L4 / unresolved risk)
    ┌──────────┐
    │ REJECTED │
    └──────────┘
         │
         ▼
  Manifest status: rejected
  Final status: REJECTED
  No collection — ever (unless new review opened as new Review ID)
```

### Rejected

| | |
|--|--|
| **Meaning** | Source must not be collected or used |
| **Manifest** | `status: rejected`; reason in `notes` |
| **Legal file** | `Final status: REJECTED`; rationale documented |
| **Who acts** | Legal counsel or data lead (L4 auto-reject) |
| **Follow-up** | Archive review; do not delete (audit trail) |

**Triggers for rejection:**

- L4 classification confirmed  
- ML training explicitly prohibited in verified terms  
- Unable to verify license after good-faith effort  
- PII or regulated content cannot be mitigated  
- Executive or legal risk acceptance denied  

### Re-open review

New source scope or new terms → **new Review ID**; do not overwrite REJECTED records.

---

## Approved With Conditions

Intermediate approval common for L2/L3 and government sources:

| Example condition | Effect |
|-------------------|--------|
| Internal training only | Training Allowed ✅ · Public weight release ❌ |
| Attribution required | NOTICE file + model card citation |
| No bulk automated download | Manual or API-only collection method |
| Subset only | Manifest lists allowed paths/datasets |
| Refresh required every N months | `valid_until` on manifest |

Conditions **must** appear in:

1. Legal review file  
2. Manifest `notes`  
3. Experiment configs (Phase 5+)  

---

## Gate Matrix

| Status | Collect | Process | Train | Public release |
|--------|---------|---------|-------|----------------|
| Proposed | ❌ | ❌ | ❌ | ❌ |
| Legal Review | ❌ | ❌ | ❌ | ❌ |
| Approved | ⚠️ pending Collection Allowed flag | ❌ | ❌ | ❌ |
| Collection Allowed | ✅ | ❌ | ❌ | ❌ |
| Processing Allowed | ✅ | ✅ | ❌ | ❌ |
| Training Allowed | ✅ | ✅ | ✅ | ⚠️ separate legal |
| Rejected | ❌ | ❌ | ❌ | ❌ |

---

## Integration Checklist (per dataset)

- [ ] Manifest `{slug}.yaml` exists  
- [ ] `{slug}-license-review.md` exists  
- [ ] Review linked from manifest `notes` or `license_text_ref`  
- [ ] LICENSING_GUIDE L-class confirmed by legal (not planning estimate)  
- [ ] CODEOWNERS review on `docs/legal/` and `data/` paths  
- [ ] Collection Allowed checked before ingest  
- [ ] Benchmark holdout dedupe before Training Allowed  

---

## First Source in Pipeline

| Source | Review | Workflow state |
|--------|--------|----------------|
| Vision 2030 Official Publications | [vision2030-license-review.md](licenses/vision2030-license-review.md) | **PENDING REVIEW** — collection **blocked** |

---

## Related Documents

- [licenses/template-license-review.md](licenses/template-license-review.md)
- [DATA_ACQUISITION_PLAN.md](../DATA_ACQUISITION_PLAN.md) — Phase A  
- [DATA_RISKS.md](../DATA_RISKS.md)
- [DECISIONS.md](../DECISIONS.md) — ADR-002, ADR-004
