# License Review — Vision 2030 Official Publications

> **Disclaimer:** This document is an internal review worksheet. It is **not legal advice**. No rights or permissions are asserted until verified by qualified legal counsel and recorded below.

---

## Record Metadata

| Field | Value |
|-------|-------|
| **Review ID** | LR-2026-001 |
| **Dataset / source name** | Vision 2030 Official Publications |
| **Manifest reference** | `data/datasets/manifests/vision2030.yaml` |
| **Tier** | 1 (Must-have) |
| **Review opened** | 2026-06-08 |
| **Last updated** | 2026-06-08 |
| **Reviewer (legal)** | _Unassigned — `@TBD-legal-counsel`_ |
| **Reviewer (data)** | _Unassigned — `@TBD-data-lead`_ |

---

## Source Identification

| Field | Value |
|-------|-------|
| **Official source URL** | https://www.vision2030.gov.sa/ |
| **Terms of use URL** | _To be identified and verified by legal counsel — not confirmed in Phase A-0_ |
| **Copyright / policy URL** | _To be identified and verified by legal counsel — not confirmed in Phase A-0_ |
| **Rights holder (expected)** | Kingdom of Saudi Arabia / relevant government entities — **not verified** |
| **Jurisdiction** | Kingdom of Saudi Arabia |

---

## License Summary

**Status:** _Not yet verified._

Planning notes for legal review ( **not conclusions** ):

- Source is an official government program website publishing policy, program, and promotional materials about Vision 2030.  
- Actual terms governing reuse, scraping, machine learning, and redistribution **must be read from official pages** (or obtained in writing) before any collection.  
- Subpages, PDFs, and third-party embedded content may be subject to **different** terms — each content type may require separate review.  
- Provisional planning class in acquisition plan: **L1** — **must not be treated as confirmed** until this review is complete.

**License text excerpt:** _None captured in Phase A-0. Counsel to attach snapshot or quotation upon review._

---

## Use Permissions (Verification Required)

| Question | Status |
|----------|--------|
| **Commercial use allowed?** | **Unknown if not verified** |
| **ML / AI training allowed?** | **Unknown if not verified** |
| **Redistribution of dataset allowed?** | **Unknown if not verified** |
| **Redistribution of model weights trained on this data allowed?** | **Unknown if not verified** |
| **Attribution required?** | **Unknown if not verified** |
| **Share-alike / copyleft obligations?** | **Unknown if not verified** |

---

## Provisional License Class (Planning Only)

| Field | Value |
|-------|-------|
| **Provisional class (manifest)** | L1 — _planning estimate only_ |
| **Confirmed class (legal)** | _Pending — do not use for gates_ |

---

## Risk Assessment

| Dimension | Assessment |
|-----------|------------|
| **Legal risk level (operational)** | **Medium** — pending terms verification |
| **Rationale** | Government site with mixed PDF/HTML assets; ML use not confirmed; potential copyright in images/design; third-party links may appear |
| **Privacy risk** | Low expected for public policy text — confirm no PII in collected samples |
| **Regulatory risk** | Medium — confirm compliance with applicable KSA regulations on government content reuse |
| **Release impact** | Public model release may require additional clearance beyond training — **unknown until verified** |

---

## Legal Notes

_Space for legal counsel — Phase A-0: intentionally empty of conclusions._

- [ ] Official terms-of-use and copyright pages located and snapshotted  
- [ ] ML/training clause identified (or confirmed absent — counsel to interpret)  
- [ ] PDF vs HTML rights assessed separately if needed  
- [ ] Conflict check with Qwen base model license for combined release  
- [ ] Conflict check with ADR-002 external storage policy  
- [ ] Written sign-off attached (future: `approvals/` or external vault)  

---

## Required Follow-Up Actions

| # | Action | Owner | Due | Done |
|---|--------|-------|-----|------|
| 1 | Locate and snapshot official terms / copyright / open-use pages | Legal counsel | TBD | [ ] |
| 2 | Confirm whether automated access or bulk download is permitted | Legal counsel | TBD | [ ] |
| 3 | Confirm ML training and fine-tuning permissions explicitly | Legal counsel | TBD | [ ] |
| 4 | Confirm redistribution rights (data shards and model weights) | Legal counsel | TBD | [ ] |
| 5 | Assign confirmed L0–L4 class; update manifest `license` field | Legal + Data | TBD | [ ] |
| 6 | If APPROVED WITH CONDITIONS, document conditions in manifest `notes` | Data lead | TBD | [ ] |
| 7 | Update [APPROVAL_WORKFLOW.md](../APPROVAL_WORKFLOW.md) status trail | Data lead | TBD | [ ] |

---

## Approval Block

| Role | Name | Date | Signature / ticket |
|------|------|------|---------------------|
| Legal counsel | _Pending_ | — | — |
| Data lead | _Pending_ | — | — |
| Executive sponsor (Tier 1) | _Pending_ | — | — |

---

## Workflow Status

| Gate | Status |
|------|--------|
| Proposed | ✅ Manifest exists (`vision2030.yaml`, `status: proposed`) |
| Legal Review | 🔄 In progress (worksheet created) |
| Approved | ❌ Not reached |
| Collection Allowed | ❌ **Blocked** |
| Processing Allowed | ❌ **Blocked** |
| Training Allowed | ❌ **Blocked** |

---

## Final Status

```
PENDING REVIEW
```

**No collection, processing, or training on this source is permitted until Final status is updated to APPROVED or APPROVED WITH CONDITIONS by legal counsel and recorded in this file and the manifest.**

---

## Change Log

| Date | Change | Author |
|------|--------|--------|
| 2026-06-08 | Initial review worksheet created (Phase A-0) | ArabArenaAI data program |
