# License Review — [DATASET NAME]

> **Disclaimer:** Internal worksheet only — **not legal advice**. Do not mark permissions as Yes/No until verified by qualified legal counsel.

---

## Record Metadata

| Field | Value |
|-------|-------|
| **Review ID** | LR-YYYY-NNN |
| **Dataset / source name** | _[Name]_ |
| **Manifest reference** | `data/datasets/manifests/[slug].yaml` |
| **Tier** | _1 / 2 / 3_ |
| **Review opened** | YYYY-MM-DD |
| **Last updated** | YYYY-MM-DD |
| **Reviewer (legal)** | _@TBD-legal-counsel_ |
| **Reviewer (data)** | _@TBD-data-lead_ |

---

## Source Identification

| Field | Value |
|-------|-------|
| **Official source URL** | _https://..._ |
| **Terms of use URL** | _https://... or "To be verified"_ |
| **Copyright / policy URL** | _https://... or "To be verified"_ |
| **Open-data license URL (if separate)** | _https://... or N/A_ |
| **Rights holder** | _[Entity] — verify_ |
| **Jurisdiction** | _SA / GCC / MULTI / GLOBAL_ |

---

## License Summary

**Status:** _Not yet verified / Partially verified / Verified [date]_

_Planning notes (not legal conclusions):_

- _Brief description of source and content types_  
- _Provisional L-class from acquisition plan: L_ — planning only_  
- _Known complexities: PDFs, user content, mixed licenses, etc._  

**License text excerpt:** _Counsel to attach snapshot path or quoted excerpt after review._

**Snapshot storage:** _Path under `docs/legal/licenses/[slug]/` or external vault ref_

---

## Use Permissions (Verification Required)

| Question | Status |
|----------|--------|
| **Commercial use allowed?** | Yes / No / **Unknown if not verified** |
| **ML / AI training allowed?** | Yes / No / **Unknown if not verified** |
| **Redistribution of dataset allowed?** | Yes / No / Conditional / **Unknown if not verified** |
| **Redistribution of model weights allowed?** | Yes / No / Conditional / **Unknown if not verified** |
| **Attribution required?** | Yes / No / **Unknown if not verified** |
| **Share-alike / copyleft obligations?** | Yes / No / **Unknown if not verified** |
| **Territorial restrictions?** | Yes / No / **Unknown if not verified** |

---

## Provisional vs Confirmed Classification

| Field | Value |
|-------|-------|
| **Provisional class (planning)** | L_ |
| **Confirmed class (legal)** | _Pending_ |

See [LICENSING_GUIDE.md](../../LICENSING_GUIDE.md) for L0–L4 definitions.

---

## Risk Assessment

| Dimension | Assessment |
|-----------|------------|
| **Legal risk level** | Low / Medium / High / Critical |
| **Rationale** | _Operational notes — not legal opinion_ |
| **Privacy risk** | Low / Medium / High |
| **Regulatory risk** | Low / Medium / High |
| **Release impact** | _API-only / weights TBD / unknown_ |

---

## Legal Notes

_Counsel workspace — conclusions and citations only after review._

- [ ] Terms located and snapshotted  
- [ ] ML/training clause addressed  
- [ ] Attribution / NOTICE requirements documented  
- [ ] Qwen base license compatibility assessed (if training planned)  
- [ ] PDPL / data protection assessed (if personal data possible)  
- [ ] Sign-off recorded  

---

## Required Follow-Up Actions

| # | Action | Owner | Due | Done |
|---|--------|-------|-----|------|
| 1 | | | | [ ] |
| 2 | | | | [ ] |
| 3 | | | | [ ] |

---

## Approval Block

| Role | Name | Date | Signature / ticket |
|------|------|------|---------------------|
| Legal counsel | | | |
| Data lead | | | |
| Executive sponsor (Tier 1 only) | | | |

---

## Workflow Status

| Gate | Status |
|------|--------|
| Proposed | ☐ |
| Legal Review | ☐ |
| Approved | ☐ |
| Collection Allowed | ☐ **Blocked until Approved** |
| Processing Allowed | ☐ |
| Training Allowed | ☐ |

---

## Final Status

```
PENDING REVIEW
```

_Allowed values: `PENDING REVIEW` · `APPROVED` · `APPROVED WITH CONDITIONS` · `REJECTED` · `DEPRECATED`_

**Conditions (if APPROVED WITH CONDITIONS):**

- _List each restriction, e.g. internal training only, no weight release, attribution text, volume limits_

---

## Change Log

| Date | Change | Author |
|------|--------|--------|
| YYYY-MM-DD | Review file created | |
