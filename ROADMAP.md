# ArabArenaAI-1 Roadmap

This roadmap defines the phased delivery plan for ArabArenaAI-1 — from repository foundation through public release and the ArabArenaAI-2 successor program.

Each phase has **entry criteria**, **deliverables**, and **exit gates**. No phase should begin until the prior phase's exit gates are met.

---

## Overview

| Phase | Name | Status |
|-------|------|--------|
| 1 | Project Foundation | **In progress** |
| 2 | Dataset Collection | Planned |
| 3 | Data Cleaning | Planned |
| 4 | Evaluation Baseline | Planned |
| 5 | Fine-Tuning | Planned |
| 6 | Internal Benchmarking | Planned |
| 7 | Private Release | Planned |
| 8 | Public Release | Planned |
| 9 | ArabArenaAI-2 | Planned |

---

## Phase 1 — Project Foundation

**Goal:** Establish a production-grade repository, governance, and strategy documentation that any serious AI team can clone and execute against.

### Deliverables

- [x] Repository directory structure
- [x] README, ROADMAP, CONTRIBUTING, LICENSE, `.gitignore`
- [x] Strategy docs: DATA, MODEL, BENCHMARKS
- [x] Research notes: FUTURE_IDEAS
- [x] GitHub issue and PR templates
- [ ] Git initialization and branch protection policy (org-level)
- [ ] CI skeleton (lint + docs check) — future

### Exit Gates

- All strategy documents reviewed and approved by project leads
- No training code, model weights, or infrastructure committed
- Clear ownership assigned for Phase 2 data workstreams

---

## Phase 2 — Dataset Collection

**Goal:** Assemble a catalog of Saudi, Arabic, and licensed datasets with provenance and license metadata.

### Deliverables

- Dataset inventory manifest (`data/datasets/` with metadata JSON/CSV)
- License audit log per source
- Saudi-priority collection plan (government open data, business corpora, Arabic web subsets)
- Public and open-source dataset integration list
- Data sharing agreements template for partner contributions

### Workstreams

1. **Saudi sources** — Vision 2030 publications, open government data, licensed news/business archives
2. **Arabic corpora** — MSA news, books, Wikipedia AR, academic text
3. **Technical** — Arabic Stack Overflow mirrors, bilingual code docs, regional dev blogs
4. **Business** — startup pitch decks (licensed), entrepreneurship content, formal correspondence templates

### Exit Gates

- Minimum viable corpus catalog documented with license class per row
- No dataset ingested without recorded license and retention policy
- Legal review sign-off for restricted sources

---

## Phase 3 — Data Cleaning

**Goal:** Transform raw corpora into normalized, deduplicated, quality-scored training-ready shards.

### Deliverables

- Cleaning pipeline specifications (not necessarily full code yet — specs first)
- Arabic normalization rules (Unicode, diacritics policy, RTL)
- Deduplication strategy (exact + fuzzy, cross-source)
- Quality scoring rubric applied to sample batches
- Train/val/test splits with documented leakage checks
- Processed data under `data/datasets/processed/` (gitignored; stored in object storage)

### Standards

See [docs/DATA_STRATEGY.md](docs/DATA_STRATEGY.md) for full cleaning and annotation standards.

### Exit Gates

- Processed shards pass quality threshold (≥ agreed score on audit sample)
- Provenance chain from raw → processed is reproducible
- PII and sensitive content redaction verified on sample

---

## Phase 4 — Evaluation Baseline

**Goal:** Run the **base** Qwen3-30B-A3B-Instruct model against ArabArena benchmark suites and establish numeric baselines.

### Deliverables

- Benchmark harness specification and implementation
- Baseline scores for all categories in [docs/BENCHMARKS.md](docs/BENCHMARKS.md)
- Evaluation reports under `evaluation/reports/`
- Regression test set frozen for future fine-tune comparisons

### Categories (initial)

- Arabic reasoning
- Saudi knowledge
- Business knowledge
- Programming
- Summarization
- Translation (AR ↔ EN)
- Long-context understanding

### Exit Gates

- Reproducible baseline run documented (hardware, seed, prompt templates)
- All category scores published internally
- Known failure modes cataloged for Phase 5 targeting

---

## Phase 5 — Fine-Tuning

**Goal:** Fine-tune Qwen3-30B-A3B-Instruct on cleaned regional data using LoRA (or agreed PEFT method).

### Deliverables

- Training configs under `training/configs/`
- Experiment logs under `training/experiments/`
- LoRA adapters under `models/` (gitignored; artifact registry)
- Model card documenting data mix, hyperparameters, and limitations
- Post-train eval on frozen regression set (Phase 4 comparison)

### Constraints

- No full-weight training unless explicitly approved (cost and license review)
- Checkpoint retention and versioning policy enforced
- Training data snapshot ID recorded per experiment

### Exit Gates

- Measurable improvement over Phase 4 baseline on Saudi + Arabic primary categories
- No regression beyond agreed tolerance on programming / global knowledge
- Internal model card approved

---

## Phase 6 — Internal Benchmarking

**Goal:** Compare ArabArenaAI-1 against frontier closed and open models under identical benchmark conditions.

### Comparison Targets

- OpenAI GPT (frontier tier at time of eval)
- Anthropic Claude
- Google Gemini
- DeepSeek

### Deliverables

- Head-to-head score tables per benchmark category
- Cost and latency comparison (where API access applies)
- Qualitative error analysis (Arabic fluency, Saudi factual accuracy, hallucination patterns)
- Go/no-go recommendation for private release

### Exit Gates

- Benchmark methodology peer-reviewed internally
- ArabArenaAI-1 wins or ties on **Saudi knowledge** and **Arabic reasoning** vs at least two comparators
- Documented known weaknesses with mitigation plan

---

## Phase 7 — Private Release

**Goal:** Deploy ArabArenaAI-1 to trusted partners, pilots, and internal products under controlled access.

### Deliverables

- Private model access policy (API keys, rate limits, audit logging)
- Inference serving specification under `inference/`
- Partner onboarding guide and acceptable use policy
- Feedback collection pipeline for Phase 8 hardening

### Exit Gates

- Security review completed
- Incident response process defined
- Minimum N partner pilot weeks with feedback incorporated

---

## Phase 8 — Public Release

**Goal:** Release ArabArenaAI-1 to the public under a clear license and model card.

### Deliverables

- Public model weights and/or hosted API (per license strategy)
- Published benchmark results and limitations
- Responsible AI statement (bias, safety, known failure modes)
- Community contribution pathways (data, eval, adapters)

### Exit Gates

- Legal and license review for weight release
- Model card and safety documentation published
- Support and maintenance commitment defined

---

## Phase 9 — ArabArenaAI-2

**Goal:** Begin the next-generation program — expanded data flywheel, architecture research, and path toward an independent foundation model.

### Focus Areas

- Pretraining data scale-up (Saudi + GCC weighted)
- Architecture evaluation (MoE, dense, context length, inference cost)
- Multimodal exploration (if aligned with product strategy)
- RAG, agents, and enterprise layers — see [research/FUTURE_IDEAS.md](research/FUTURE_IDEAS.md)
- Governance model for an independent ArabArenaAI model family

### Deliverables

- ArabArenaAI-2 research charter
- Data flywheel design (partner contributions, synthetic data policy)
- Architecture decision record (ADR) set
- Phase 1 ArabArenaAI-2 roadmap draft

---

## Dependencies & Critical Path

```
Phase 1 ──► Phase 2 ──► Phase 3 ──► Phase 4 ──► Phase 5 ──► Phase 6 ──► Phase 7 ──► Phase 8
                                                                                        │
                                                                                        ▼
                                                                                   Phase 9
```

**Critical path risks:** data licensing delays (Phases 2–3), GPU availability (Phases 4–5), benchmark fairness disputes (Phase 6).

---

## Version History

| Version | Date | Notes |
|---------|------|-------|
| 0.1.0 | 2026-06-08 | Initial roadmap — foundation phase |
