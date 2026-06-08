# ArabArenaAI-1

**Saudi-first · Gulf-first · Arabic-first · Business-aware · Developer-friendly**

ArabArenaAI-1 is the first milestone in the ArabArenaAI model family — a standalone Arabic language model initiative built for the Gulf, designed for business, entrepreneurship, and software engineering, with a long-term path toward an independent foundation model.

This is not a generic chatbot wrapper. It is a deliberate, region-aligned AI program with clear priorities, measurable benchmarks, and a production-minded roadmap.

---

## Vision

The Arab world deserves AI systems that understand **how people actually work, communicate, and build** — not models that treat Arabic as an afterthought or Saudi Arabia as a footnote.

ArabArenaAI-1 exists to:

- Put **Saudi Arabia and the GCC** at the center of model behavior and evaluation
- Treat **Arabic** (Modern Standard Arabic, Gulf dialects, and formal business Arabic) as a first-class language
- Excel at **business, entrepreneurship, and technical content** relevant to the regional ecosystem
- Serve as the **foundation** for a future ArabArenaAI model family — independent, auditable, and deployable

**Long-term mission:** evolve from a fine-tuned regional specialist into a fully independent ArabArenaAI foundation model lineage, owned and governed with regional context at its core.

---

## Why ArabArenaAI-1 Exists

Global frontier models are strong on general knowledge but consistently underperform on:

- Saudi government services, Vision 2030, and local regulatory context
- Gulf business terminology, startup ecosystems, and formal Arabic correspondence
- Saudi and Khaleeji dialects in practical, mixed-language workflows
- Regional developer workflows (Arabic docs, bilingual code comments, local SaaS patterns)

ArabArenaAI-1 closes that gap systematically — through **data strategy**, **model selection**, **rigorous benchmarking**, and **phased release** — rather than prompt engineering alone.

---

## Core Principles (Priority Order)

| Priority | Domain |
|----------|--------|
| 1 | Saudi Arabia |
| 2 | GCC Countries |
| 3 | Arabic Language |
| 4 | Business & Entrepreneurship |
| 5 | Software Engineering |
| 6 | Global Knowledge |

The model should deeply understand Saudi culture, government services, Vision 2030, business terminology, startup ecosystems, formal and dialectal Arabic, and technical/programming content — while retaining useful global knowledge as a lower-priority layer.

---

## Project Principles

These principles govern every phase — from dataset selection to public release:

| Principle | Commitment |
|-----------|------------|
| **Quality over quantity** | Curated, licensed, high-scoring data beats large noisy crawls. Reject corpora that fail quality gates. |
| **Arabic-first** | Arabic reasoning, register, and typography are designed in — not translated from English behavior. |
| **Saudi-first** | Saudi context is the default for data weighting, evaluation, and product behavior. |
| **Legally compliant datasets only** | No source enters the pipeline without a recorded license and approval (see [docs/DATA_STRATEGY.md](docs/DATA_STRATEGY.md)). |
| **Reproducible experiments** | Every run logs model ID, data snapshot, config hash, seed, and prompt template version. |
| **Transparent benchmarking** | Scores, limitations, and methodology are published honestly — no benchmark theater. |

Full vision and non-goals: [docs/VISION.md](docs/VISION.md). Architectural decisions: [docs/DECISIONS.md](docs/DECISIONS.md). KPIs: [docs/METRICS.md](docs/METRICS.md).

---

## Saudi-First Strategy

**Saudi-first** means Saudi context is the default lens — not an optional locale pack.

- **Evaluation:** Saudi knowledge and Gulf-relevant scenarios are primary benchmark categories, not subsets of "Arabic QA"
- **Data:** Saudi-authored and Saudi-relevant corpora are prioritized in collection, licensing review, and quality gates
- **Product behavior:** Responses assume Saudi regulatory, cultural, and business norms unless the user specifies otherwise
- **Roadmap:** Public releases are gated on Saudi benchmark thresholds before broader GCC generalization claims

---

## Arabic-First Strategy

**Arabic-first** means Arabic is designed in from day one — not translated from English behavior.

- **MSA + dialect coverage:** Modern Standard Arabic for formal use; Saudi and Gulf dialects where conversational fidelity matters
- **Script and typography:** Correct Arabic rendering, punctuation, and mixed Arabic–English technical text
- **Reasoning in Arabic:** Benchmarks measure Arabic reasoning directly, not English-chain-of-thought with Arabic output
- **Data hygiene:** Cleaning, deduplication, and annotation standards are Arabic-aware (RTL, morphological richness, code-switching)

See [docs/DATA_STRATEGY.md](docs/DATA_STRATEGY.md) and [docs/BENCHMARKS.md](docs/BENCHMARKS.md) for details.

---

## Base Model

**Selected base:** [Qwen3-30B-A3B-Instruct](https://huggingface.co/Qwen)

Qwen3-30B-A3B-Instruct is the starting checkpoint for Phase 1 baseline runs and Phase 5 LoRA fine-tuning. Rationale, comparisons, licensing, and migration path are documented in [docs/MODEL_STRATEGY.md](docs/MODEL_STRATEGY.md).

> **Note:** No models are downloaded or fine-tuned in the foundation phase. The base model is declared strategy only until Phase 1 execution.

---

## Model Roadmap

| Phase | Milestone | Outcome |
|-------|-----------|---------|
| 1 | Project Foundation | Repository, docs, governance |
| 2 | Dataset Collection | Saudi + Arabic + licensed corpora |
| 3 | Data Cleaning | Normalized, auditable training-ready data |
| 4 | Evaluation Baseline | Base Qwen3 scores on ArabArena benchmarks |
| 5 | Fine-Tuning | LoRA / instruction tuning on regional data |
| 6 | Internal Benchmarking | Compare vs GPT, Claude, Gemini, DeepSeek |
| 7 | Private Release | Controlled access for partners and pilots |
| 8 | Public Release | Open weights and/or API per license strategy |
| 9 | ArabArenaAI-2 | Next-generation architecture and data flywheel |

Full timeline: [ROADMAP.md](ROADMAP.md)

---

## Architecture Roadmap

```
┌─────────────────────────────────────────────────────────────────┐
│                     ArabArenaAI Model Family                       │
├─────────────────────────────────────────────────────────────────┤
│  Phase 1–4   Foundation + Data + Baseline Eval                    │
│  Phase 5     Fine-tuned ArabArenaAI-1 (Qwen3 + regional LoRA)   │
│  Phase 6–8   Benchmarked release (private → public)             │
│  Phase 9+    ArabArenaAI-2 — expanded data, architecture study  │
├─────────────────────────────────────────────────────────────────┤
│  Future layers (see research/FUTURE_IDEAS.md):                    │
│  RAG · Agents · Memory · Multi-model routing · Arabic embeddings │
└─────────────────────────────────────────────────────────────────┘
```

**Near-term stack (planned, not implemented):**

- **Data:** `data/datasets/` — raw ingestion, processed shards, manifest-driven provenance
- **Training:** `training/` — configs, experiment tracking, LoRA adapters under `models/`
- **Evaluation:** `evaluation/` — benchmark suites, scored reports, regression gates
- **Inference:** `inference/` — serving interfaces (added in later phases)
- **Research:** `research/` — architecture and product experiments

---

## Repository Structure

```
ArabArenaAI-1/
├── data/datasets/          Raw and processed datasets
├── training/               Configs and experiment artifacts
├── evaluation/             Benchmarks and evaluation reports
├── inference/              Inference interfaces (future)
├── models/                 Model cards and adapter weights (future)
├── scripts/                Operational and data scripts (future)
├── research/               Long-horizon research notes
├── docs/                   Strategy and technical documentation
├── .github/                Issue and PR templates
└── tests/                  Test suite (future)
```

> **Storage policy:** Large datasets, model weights, checkpoints, and generated artifacts are not stored in this repository. They will be managed through external storage such as Hugging Face Hub, Hugging Face Datasets, Cloudflare R2, or S3.

---

## Documentation Index

| Document | Description |
|----------|-------------|
| [ROADMAP.md](ROADMAP.md) | Phased delivery plan (Phases 1–9) |
| [docs/VISION.md](docs/VISION.md) | Mission, success/failure, non-goals |
| [docs/DECISIONS.md](docs/DECISIONS.md) | Architectural decision records (ADR) |
| [docs/METRICS.md](docs/METRICS.md) | KPIs and release gate thresholds |
| [docs/DATA_STRATEGY.md](docs/DATA_STRATEGY.md) | Data sources, licensing, quality, cleaning |
| [docs/DATASET_MANIFEST_TEMPLATE.md](docs/DATASET_MANIFEST_TEMPLATE.md) | Per-dataset manifest schema |
| [docs/MODEL_STRATEGY.md](docs/MODEL_STRATEGY.md) | Base model selection and comparisons |
| [docs/BENCHMARKS.md](docs/BENCHMARKS.md) | Evaluation categories and scoring |
| [research/FUTURE_IDEAS.md](research/FUTURE_IDEAS.md) | RAG, agents, foundation model path |
| [CONTRIBUTING.md](CONTRIBUTING.md) | How to contribute |

---

## Current Status

**Phase 1 — Project Foundation** ✅ (structure and documentation)

Training code, model downloads, inference servers, Docker, and GPU infrastructure are **intentionally out of scope** for this phase.

---

## Future Plans

- Build a Saudi- and GCC-weighted instruction and pretraining corpus with full license audit trails
- Fine-tune Qwen3-30B-A3B-Instruct with LoRA for regional specialization
- Publish an internal benchmark suite covering Arabic reasoning, Saudi knowledge, business, and code
- Release privately to partners, then publicly under a clear license
- Begin ArabArenaAI-2 research: data flywheel, architecture options, and optional RAG/agent layers

---

## Contributing

We welcome contributions aligned with our Saudi-first and Arabic-first principles. Please read [CONTRIBUTING.md](CONTRIBUTING.md) before opening a pull request.

---

## License

This repository is licensed under the Apache License 2.0. See [LICENSE](LICENSE) for details.

Model weights and third-party datasets may carry separate licenses — always consult [docs/DATA_STRATEGY.md](docs/DATA_STRATEGY.md) and [docs/MODEL_STRATEGY.md](docs/MODEL_STRATEGY.md) before use.

---

## Contact & Governance

> _Placeholder for official project contact, security disclosure, and governance committee — to be added before public release._

---

**ArabArenaAI-1** — Building AI that understands the Gulf, speaks Arabic natively, and serves builders and businesses.
