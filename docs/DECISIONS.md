# Architectural Decision Records (ADR)

This log tracks **major architectural and strategic decisions** for ArabArenaAI-1. Every significant choice that affects data, models, evaluation, release, or infrastructure should be recorded here before implementation.

---

## How to Use This Document

1. Add a new entry at the **top** of the Decision Log (newest first).
2. Assign a sequential ID: `ADR-001`, `ADR-002`, …
3. Fill in every field — incomplete records block Phase gate reviews.
4. Link related PRs, issues, and strategy docs.
5. Do **not** delete superseded decisions; mark them **Superseded by ADR-NNN**.

---

## Entry Template

Copy this block for each new decision:

```markdown
### ADR-NNN — [Short title]

| Field | Value |
|-------|-------|
| **Date** | YYYY-MM-DD |
| **Status** | Proposed · Accepted · Deprecated · Superseded |
| **Decision** | What was decided? One clear statement. |
| **Reason** | Why this decision? Tie to Saudi-first / Arabic-first goals where relevant. |
| **Alternatives considered** | Option A — rejected because … · Option B — rejected because … |
| **Consequences** | Positive outcomes, trade-offs, follow-up work, risks introduced. |
| **Owner** | Name or team |
| **Related** | Links to docs, PRs, issues |
```

---

## Decision Log

### ADR-004 — Saudi-first knowledge strategy

| Field | Value |
|-------|-------|
| **Date** | 2026-06-08 |
| **Status** | Accepted |
| **Decision** | Prioritize **Saudi-specific knowledge sources** over generic Arabic or global corpora in dataset inventory, collection order, training mix, and benchmark design. Target initial training mix weighting: **~40% Saudi** · **~15% GCC** · **~25% Arabic (non-SA)** · **~10% business** · **~10% programming** — recalibrated after Phase 4 baseline. |
| **Reason** | ArabArenaAI-1's differentiated value is Saudi and Gulf fidelity, not generic multilingual capability. Generic corpora (e.g. Arabic Wikipedia alone) cannot ground Vision 2030, Saudi government services, or local business norms. Saudi-first weighting aligns data investment with [VISION.md](VISION.md) and [METRICS.md](METRICS.md) release gates. |
| **Alternatives considered** | **Arabic-only weighting (no SA priority)** — rejected; fails core mission. **Equal mix across all regions** — rejected; dilutes Saudi signal. **Saudi-only (exclude GCC/global)** — rejected; loses programming regression and bilingual technical coverage. **RAG-only without fine-tune** — deferred; may complement but not replace regional weights. |
| **Consequences** | Manifest inventory must tag `country: SA` sources first (`saudi_open_data`, `vision2030` before `wikipedia_ar`). Collection budget and legal review capacity allocated to SA sources first. Wikipedia and global code corpora are **supporting**, not primary. Benchmark Saudi category is a **release gate**, not optional. Mix ratios must be recorded in experiment configs (Phase 5). |
| **Owner** | Data + ML leads (placeholder) |
| **Related** | [DATA_STRATEGY.md](DATA_STRATEGY.md) · [DATA_PIPELINE.md](DATA_PIPELINE.md) · [LICENSING_GUIDE.md](LICENSING_GUIDE.md) · [../data/datasets/manifests/](../data/datasets/manifests/) |

---

### ADR-001 — Base model: Qwen3-30B-A3B-Instruct

| Field | Value |
|-------|-------|
| **Date** | 2026-06-08 |
| **Status** | Accepted |
| **Decision** | Use **Qwen3-30B-A3B-Instruct** as the base checkpoint for baseline evaluation (Phase 4) and LoRA fine-tuning (Phase 5). |
| **Reason** | Strong Arabic performance for its size class; instruction-tuned variant reduces alignment lift; MoE efficiency (~3B active) improves inference cost for Phase 7 pilots; open weights with mature PEFT ecosystem. |
| **Alternatives considered** | **Llama 3.x** — strong ecosystem but Community License constraints and weaker Arabic-centric pretrain. **DeepSeek** — excellent reasoning/code; retained as Phase 6 comparator and future routing candidate. **Gemma 3** — efficient at small scale but weaker Arabic/regional knowledge. |
| **Consequences** | Must comply with Qwen license at weight download and public release. MoE serving requires compatible runtime (Phase 7). Regional specialization still depends entirely on Phase 2–5 data program. Migration path to ArabArenaAI-2 documented in [MODEL_STRATEGY.md](MODEL_STRATEGY.md). |
| **Owner** | ML Architecture (placeholder) |
| **Related** | [MODEL_STRATEGY.md](MODEL_STRATEGY.md) · [ROADMAP.md](../ROADMAP.md) Phase 4–5 |

---

### ADR-002 — No large artifacts in git

| Field | Value |
|-------|-------|
| **Date** | 2026-06-08 |
| **Status** | Accepted |
| **Decision** | Datasets, model weights, checkpoints, and generated outputs are **never** committed to this repository. External storage only (Hugging Face Hub/Datasets, R2, S3). |
| **Reason** | Prevents repo bloat, license leakage of raw corpora, accidental secret/PII commits, and non-reproducible “works on my machine” weight dumps. |
| **Alternatives considered** | **Git LFS for weights** — rejected due to cost, review friction, and license audit difficulty. **Monorepo with data** — rejected; violates compliance workflow. |
| **Consequences** | All pipelines must reference external URIs + manifest IDs. CI cannot assume local data. `.gitignore` and README storage policy are authoritative. |
| **Owner** | MLOps (placeholder) |
| **Related** | [../.gitignore](../.gitignore) · [DATA_STRATEGY.md](DATA_STRATEGY.md) · [DATASET_MANIFEST_TEMPLATE.md](DATASET_MANIFEST_TEMPLATE.md) |

---

### ADR-003 — Apache 2.0 for repository code

| Field | Value |
|-------|-------|
| **Date** | 2026-06-08 |
| **Status** | Accepted |
| **Decision** | License all **repository source code and documentation** under **Apache License 2.0**. Model weights and datasets carry **separate** licenses. |
| **Reason** | Permissive, enterprise-friendly, patent grant clarity, standard for open ML tooling repos. |
| **Alternatives considered** | **MIT** — simpler but no explicit patent grant. **Proprietary** — rejected for Phase 8 public-release alignment and community contribution path. |
| **Consequences** | Model card and release process must document license stack (base model + data + adapter). Cannot assume Apache applies to weights. |
| **Owner** | Legal / Governance (placeholder) |
| **Related** | [../LICENSE](../LICENSE) · [MODEL_STRATEGY.md](MODEL_STRATEGY.md) |

---

## Pending Decisions (Phase 2+)

| Topic | Target phase | Notes |
|-------|--------------|-------|
| Corpus mix ratios (SA / GCC / AR / business / code) | Phase 2 | **ADR-004 accepted** — monitor in manifests |
| LoRA rank and target modules | Phase 5 | After Phase 4 baseline |
| Inference runtime (vLLM vs TGI vs custom) | Phase 7 | After adapter size known |
| Public release: weights vs API-only | Phase 8 | Legal + business review |

---

## Related Documents

- [VISION.md](VISION.md) — mission and non-goals
- [MODEL_STRATEGY.md](MODEL_STRATEGY.md) — model selection detail
- [DATA_STRATEGY.md](DATA_STRATEGY.md) — data governance
- [METRICS.md](METRICS.md) — KPI definitions tied to release gates
