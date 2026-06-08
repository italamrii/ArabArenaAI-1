# Licensing Guide — ArabArenaAI-1

This guide defines the **L0–L4 license classification system** for all datasets and external assets used in ArabArenaAI-1. Every manifest must assign exactly one class. When in doubt, **classify up** (more restrictive) until legal review confirms otherwise.

Related: [DATA_STRATEGY.md](DATA_STRATEGY.md) · [../data/datasets/manifests/README.md](../data/datasets/manifests/README.md) · [DATA_PIPELINE.md](DATA_PIPELINE.md)

---

## Classification Overview

| Class | Name | Training | Redistribution | Review required |
|-------|------|----------|----------------|-----------------|
| **L0** | Public domain | ✅ | ✅ | Data lead |
| **L1** | Open commercial | ✅ | ✅ (per terms) | Data lead |
| **L2** | Attribution required | ✅ | ✅ with attribution | Data lead + attribution plan |
| **L3** | Restricted review required | Conditional | Conditional | **Legal counsel** |
| **L4** | Forbidden | ❌ | ❌ | Auto-reject |

---

## L0 — Public Domain

**Definition:** Works with no copyright restriction — expired copyright, explicit public domain dedication, or CC0-equivalent waiver.

**Examples (verify at ingest):**

- CC0 datasets with verified waiver
- Government works explicitly declared public domain (jurisdiction-specific)
- Facts and raw statistics without creative expression (case-by-case)

**Requirements:**

- Document jurisdiction and legal basis in manifest `notes`
- Snapshot license page or dedication text in `docs/legal/licenses/`

**Training / redistribution:** Allowed unless combined with other restricted data that taints the mix.

---

## L1 — Open Commercial

**Definition:** Permissive open licenses allowing commercial use and ML training without attribution mandates beyond license text (or minimal notice).

**Examples (verify at ingest):**

- Apache 2.0, MIT, BSD
- Open Data Portal terms explicitly permitting commercial reuse
- Hugging Face datasets tagged permissively **after manual verification**

**Requirements:**

- Record full license name in manifest
- Confirm **no copyleft** clause that affects model weights (unless legal approves)
- Per-repo license scan for aggregated code corpora

**Training / redistribution:** Allowed subject to license notice retention in documentation.

---

## L2 — Attribution Required

**Definition:** Licenses requiring **attribution**, notice preservation, or share-alike on **derivatives of the dataset** (not necessarily the model — interpret carefully).

**Examples (verify at ingest):**

- CC BY 4.0
- CC BY-SA 3.0 (Wikipedia Arabic)
- Open Government License variants requiring attribution

**Requirements:**

- **Attribution plan** in manifest: where credits appear (model card, README, NOTICE file)
- Legal review if share-alike may apply to **model weight redistribution**
- Track all L2 sources in a central `NOTICE` file before Phase 8 release

**Training / redistribution:** Allowed with attribution; weight release may require legal sign-off for SA licenses.

---

## L3 — Restricted Review Required

**Definition:** Sources where training or redistribution rights are **unclear, limited, or contract-governed** — including research-only, non-commercial, or partner NDAs.

**Examples:**

- Research-only academic corpora
- Licensed news archives with ML addenda
- Partner data under custom Data Sharing Agreement (DSA)
- Terms of Service silent on ML training

**Requirements:**

- **Written legal approval** before collection
- DSA or license snapshot on file
- Explicit manifest flags: `training_allowed`, `redistribution_allowed`
- Often **internal-only** training; no public weight release without renegotiation

**Training / redistribution:** Only as explicitly approved in writing.

---

## L4 — Forbidden

**Definition:** Sources that **must not** be collected, stored, or used for training.

**Automatic L4 triggers:**

- Terms of Service explicitly prohibit scraping or ML training
- Unknown or unreadable license
- Pirated, leaked, or unauthorized content
- Authenticated-only systems scraped without permission
- Datasets with unresolvable PII or classified content
- Sanctions or export-control violations

**Requirements:**

- Set manifest `status: rejected`
- Document reason in `notes` for audit trail
- Do not store raw bytes even temporarily without legal override

**Training / redistribution:** **Never.**

---

## Legal Risk Field (manifest)

Complement license class with operational risk:

| Value | Meaning | Typical class |
|-------|---------|---------------|
| `low` | Clear terms; standard open source or government open data | L0–L2 |
| `medium` | Mixed licenses, large aggregations, or ambiguous ToS | L1–L3 |
| `high` | Partner contracts, news archives, or share-alike on derivatives | L3 |

High `legal_risk` requires legal review even if nominally L1.

---

## Licensing Workflow

```
                    ┌─────────────────┐
                    │ Manifest created │
                    │ license_class set│
                    └────────┬────────┘
                             │
              ┌──────────────┼──────────────┐
              ▼              ▼              ▼
           L0 / L1         L2            L3
              │              │              │
              ▼              ▼              ▼
        Data lead       Data lead +     Legal counsel
         approves      attribution plan   written approval
              │              │              │
              └──────────────┼──────────────┘
                             ▼
                    ┌─────────────────┐
         L4 ───────►│    REJECTED     │
                    └─────────────────┘
                             │
                             ▼ (approved)
                    ┌─────────────────┐
                    │ Collection may  │
                    │ proceed         │
                    └─────────────────┘
```

### Checklist before `status: approved`

- [ ] License class assigned (L0–L4)
- [ ] `source_url` points to terms or authoritative dataset page
- [ ] License text snapshot planned or stored (`docs/legal/licenses/`)
- [ ] `training_allowed` and `redistribution_allowed` explicitly set
- [ ] `legal_risk` assessed
- [ ] L2: attribution plan documented
- [ ] L3: legal ticket / approval reference in `notes`
- [ ] L4: manifest marked `rejected` — stop

---

## Model & Weight Release (Phase 8)

Public release requires a **license stack review**:

```
Final release = Qwen base license ∩ training data licenses ∩ adapter license
```

Most restrictive layer governs. L2 share-alike and L3 contractual limits are common blockers for full weight release — API-only deployment may be required.

Document outcome in model card and ADR before Phase 8.

---

## Related Documents

- [DATASET_MANIFEST_TEMPLATE.md](DATASET_MANIFEST_TEMPLATE.md)
- [DATA_PIPELINE.md](DATA_PIPELINE.md) — Stage 3 Legal Review
- [DECISIONS.md](DECISIONS.md) — ADR-002, ADR-004
- [MODEL_STRATEGY.md](MODEL_STRATEGY.md) — Qwen license
