# Legal Review — ArabArenaAI-1

This directory holds **legal review records, license snapshots, and approval workflow documentation** for all datasets and external assets used in ArabArenaAI-1.

**Nothing in this folder constitutes legal advice.** All conclusions require review by qualified legal counsel familiar with Saudi and international IP, copyright, and data protection law.

---

## Purpose of Legal Reviews

Legal reviews exist to:

1. **Prevent unlicensed collection** — no raw data ingest until approval status permits collection  
2. **Enable shippable models** — training and public release depend on a clear license stack  
3. **Document diligence** — audit trail for partners, investors, and regulators  
4. **Classify risk** — align manifests with L0–L4 per [LICENSING_GUIDE.md](../LICENSING_GUIDE.md)  
5. **Separate facts from assumptions** — unverified terms are marked **Unknown**, not guessed  

Legal review runs **in parallel with** data manifests in `data/datasets/manifests/` but is **authoritative** for collection, processing, and training gates.

---

## Directory Layout

```
docs/legal/
├── README.md                          ← This file
├── APPROVAL_WORKFLOW.md               ← Status lifecycle and gates
└── licenses/
    ├── template-license-review.md     ← Copy for each new source
    └── {dataset}-license-review.md    ← One file per source under review
```

**Future (not created in Phase A-0):**

- `licenses/{dataset}/` — PDF/HTML snapshots of terms (stored here or external vault; never raw dataset bytes)  
- `approvals/` — signed approval records (when process matures)  

---

## Dataset Approval Process

```
Manifest proposed (data team)
        │
        ▼
License review file created from template
        │
        ▼
Legal counsel review (L2+ mandatory; L1 recommended for Tier 1)
        │
        ├──► PENDING REVIEW ──► work in progress
        ├──► APPROVED ────────► collection allowed (per conditions)
        ├──► APPROVED WITH CONDITIONS ─► documented restrictions
        └──► REJECTED ────────► no collection; manifest status: rejected
```

### Step-by-step

| Step | Action | Owner |
|------|--------|-------|
| 1 | Data team opens manifest PR (`status: proposed`) | Data team |
| 2 | Create `{dataset}-license-review.md` from template | Data team |
| 3 | Record official URLs; **do not** assert rights until verified | Data team |
| 4 | Legal counsel reviews terms and fills verification fields | Legal counsel |
| 5 | Assign L0–L4 class; update `Final status` | Legal counsel |
| 6 | Data lead + legal sign approval block | Approvers |
| 7 | Update manifest: `approved_by`, `approved_date`, `status: approved` | Data lead |
| 8 | Collection may begin **only** when workflow reaches **Collection Allowed** | Data ops |

See [APPROVAL_WORKFLOW.md](APPROVAL_WORKFLOW.md) for full status definitions.

---

## License Verification Process

For each source, legal review must ** independently verify** (not assume):

| Question | Record in review file |
|----------|----------------------|
| What is the governing license or terms? | License summary (quote or link to snapshot) |
| Who is the rights holder? | Rights holder field |
| Is commercial use permitted? | Yes / No / **Unknown if not verified** |
| Is ML training permitted? | Yes / No / **Unknown if not verified** |
| Is redistribution of derivatives permitted? | Yes / No / Conditional / **Unknown if not verified** |
| Are there attribution requirements? | Yes / No / details |
| Are there territorial restrictions? | Yes / No / details |
| Snapshot date of terms reviewed | ISO-8601 date |

**Verification sources (in order of preference):**

1. Official terms-of-use / copyright page on `source_url` domain  
2. Open-data license attached to specific dataset entry  
3. Written permission or DSA (L3 sources)  
4. Legal counsel written opinion  

Until verification is complete, all use flags remain **Unknown if not verified** and `Final status` remains **PENDING REVIEW**.

---

## Risk Classification Process

Each review assigns a **legal risk level** (operational, not legal conclusion):

| Level | Meaning | Typical action |
|-------|---------|----------------|
| **Low** | Clear public/open terms expected; standard gov open data | Data lead + legal spot-check |
| **Medium** | Mixed content, PDF corpora, or ambiguous ToS | Full legal review before collection |
| **High** | L3, news archives, share-alike, or weight-release uncertainty | Written legal approval required |
| **Critical** | L4 indicators or show-stopper terms | **REJECTED** — do not collect |

Map to L0–L4 in [LICENSING_GUIDE.md](../LICENSING_GUIDE.md) after legal review — **provisional** class in manifest before review is planning only.

---

## Approval Authority

| Decision | Authority | Escalation |
|----------|-----------|------------|
| L0–L1 classification (non-Tier-1) | Data lead + legal review file | Legal counsel if disputed |
| L0–L1 Tier 1 Saudi sources | **Legal counsel** + data lead | Executive sponsor |
| L2 classification + attribution plan | **Legal counsel** + data lead | Product (release impact) |
| L3 any use | **Legal counsel** written approval | Executive sponsor |
| L4 / REJECTED | Legal counsel or data lead | None — stop |
| Public model weight release | **Legal counsel** + executive | Board if required |
| Override / waiver | ADR + executive sign-off | Per [MODEL_RELEASE_POLICY.md](../MODEL_RELEASE_POLICY.md) |

**Placeholder roles** (replace before Phase A collection):

- Legal counsel: `@TBD-legal-counsel`  
- Data lead: `@TBD-data-lead`  
- Executive sponsor: `@TBD-executive-sponsor`  

---

## Active Reviews

| Dataset | Review file | Final status |
|---------|-------------|--------------|
| Vision 2030 Official Publications | [licenses/vision2030-license-review.md](licenses/vision2030-license-review.md) | **PENDING REVIEW** |

---

## Rules (Phase A-0)

- **Do not download datasets** as part of legal review unless counsel explicitly requests snapshots of **terms pages only**  
- **Do not state** that training or commercial use is allowed unless verified and recorded  
- **Do not collect** while status is PENDING REVIEW or REJECTED  
- **Do update** manifest and review file together in the same PR when status changes  

---

## Related Documents

- [APPROVAL_WORKFLOW.md](APPROVAL_WORKFLOW.md)
- [LICENSING_GUIDE.md](../LICENSING_GUIDE.md)
- [DATA_PIPELINE.md](../DATA_PIPELINE.md) — Stage 3 Legal Review
- [DATA_RISKS.md](../DATA_RISKS.md)
- [../data/datasets/manifests/README.md](../../data/datasets/manifests/README.md)
