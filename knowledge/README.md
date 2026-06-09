# Saudi Knowledge Pack v1

Structured, auditable Saudi domain knowledge for **future RAG use** — not training data and not a live crawler.

## What this is

Saudi Knowledge Pack v1 is a small, legal-first registry of seven priority Saudi government and business domains:

| Domain | Focus |
|--------|--------|
| Qiwa | Labor-market digital services |
| Nitaqat | Saudization classification |
| Monsha'at | SME and entrepreneurship authority |
| ZATCA | Zakat, tax, customs, e-invoicing |
| MISA | Ministry of Investment |
| Etimad | Government procurement |
| Vision 2030 | National transformation roadmap |

Each domain has:

- A **manifest entry** (`manifests/saudi_knowledge_pack_v1.json`) with provenance, license status, and collection status
- A **manual seed document** (`documents/*.md`) written by the project team for structure and prototyping

## What this is not

- **Not a RAG system** — no embeddings, vector store, or retrieval pipeline yet (Phase 5.3)
- **Not a scraped corpus** — no automated collection from official sites in this phase
- **Not training data** — no fine-tuning, no bulk downloads, no model updates
- **Not legally approved for ingestion** — all sources are `proposed` or `pending_review` unless explicitly approved later

## Directory layout

```
knowledge/
├── manifests/          JSON schema + pack manifest (source registry)
├── documents/          Manual seed markdown (one file per domain)
├── sources/            Reserved for approved raw snapshots (empty in v1)
├── processed/          Reserved for chunked/normalized text (empty in v1)
├── pack_loader.py      Load + validate manifest (library)
├── validate_knowledge_pack.py   CLI validator
└── README.md           This file
```

## How it will be used later (RAG prototype)

Phase 5.3 will:

1. Load **approved** sources only from the manifest
2. Chunk documents from `documents/` and/or collected files in `sources/`
3. Build a local retrieval index for evaluation-time augmentation
4. Measure AAS lift vs. the calibrated Qwen baseline (AAS 74.09)

Until sources move to `approved` → `collected`, RAG should treat seed docs as **internal prototypes**, not production knowledge.

## Why no scraping yet

ArabArenaAI requires **license_status** and **allowed_use** on every source before collection. Several domains (especially Vision 2030) have explicit legal reviews still **PENDING REVIEW**. Scraping before approval would violate project governance and create non-auditable training/RAG data.

## Source lifecycle

```
proposed  →  pending_review  →  approved  →  collected
                ↓
             blocked (no collection)
```

| Field | Meaning |
|-------|---------|
| `license_status` | Legal clearance for use (proposed, pending_review, approved, blocked, unknown) |
| `collection_status` | Whether content has been ingested (proposed, approved, collected, blocked) |
| `collected_at` | ISO timestamp when raw material was snapshotted; `null` until collected |
| `allowed_use` | Human-readable scope (e.g., registry_only, rag_prototype, training) |

**Rules enforced by the validator:**

- Every manifest entry must reference an existing document
- Every `documents/*.md` file must have a manifest entry
- Any `collection_status: collected` entry must have `license_status` and `collected_at`

## Validate the pack

```bash
python knowledge/validate_knowledge_pack.py
```

## Related project docs

- Data licensing workflow: `docs/LICENSING_GUIDE.md`
- Approval pipeline: `docs/legal/APPROVAL_WORKFLOW.md`
- Vision 2030 legal review: `docs/legal/licenses/vision2030-license-review.md`
