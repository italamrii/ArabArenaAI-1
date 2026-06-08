# Model Strategy — ArabArenaAI-1

This document explains why **Qwen3-30B-A3B-Instruct** is the selected base model, how it compares to alternatives, and the planned migration path toward an independent ArabArenaAI model family.

---

## Decision Summary

| Attribute | Choice |
|-----------|--------|
| **Base model** | Qwen3-30B-A3B-Instruct |
| **Phase 1 action** | Declare strategy only — no download, no inference |
| **Phase 4 action** | Baseline evaluation on ArabArena benchmarks |
| **Phase 5 action** | LoRA / PEFT fine-tuning on regional data |
| **Long-term** | ArabArenaAI-2 — evaluate pretraining and architecture independence |

---

## Why Qwen3-30B-A3B-Instruct

### Strategic Fit

1. **Arabic capability** — Qwen family models consistently rank among strong open-weight performers on multilingual and Arabic benchmarks relative to size class
2. **Instruction following** — Instruct variant reduces Phase 5 alignment lift vs base pretrained-only checkpoints
3. **Efficiency (A3B MoE)** — ~30B total parameters with ~3B active per token — favorable cost/latency for inference pilots (Phase 7)
4. **Open weights** — Enables private fine-tuning, internal benchmarking, and eventual weight release subject to license
5. **Ecosystem** — Mature tooling (Transformers, vLLM, PEFT/LoRA) reduces engineering risk in Phase 4–5

### Trade-offs Accepted

- **Vendor concentration** — Alibaba Qwen lineage; migration plan required (see below)
- **MoE complexity** — Serving MoE requires compatible runtimes; ops learning curve in Phase 7
- **Not Saudi-native** — Regional specialization requires Phase 2–5 data program; base model alone is insufficient

---

## Comparison Matrix

Scores below are **qualitative strategic assessments** for ArabArenaAI-1 purposes — not reproduced benchmark numbers. Phase 4 will produce measured baselines.

| Criterion | Qwen3-30B-A3B-Instruct | Llama 3.x (70B/8B class) | DeepSeek (V3 / distill) | Gemma 3 (Google) |
|-----------|------------------------|--------------------------|-------------------------|------------------|
| **Arabic fluency** | Strong for open-weight tier | Moderate; improved in 3.x but English-centric pretrain | Strong; competitive on multilingual | Moderate; smaller tiers weaker on dialect |
| **Instruction following** | Strong (Instruct) | Strong (Instruct variants) | Strong | Strong (Instruct) |
| **Saudi/GCC knowledge (zero-shot)** | Moderate | Moderate–Low | Moderate | Low–Moderate |
| **Business / code** | Strong | Strong | Very strong (code/reasoning) | Moderate |
| **License (weights)** | Qwen license (permissive with terms — verify) | Llama Community License (restrictions apply) | DeepSeek license (verify version) | Gemma Terms of Use |
| **Fine-tune friendliness** | High (LoRA ecosystem) | High | High | High |
| **Inference cost (MoE/Dense)** | Favorable (A3B active) | 8B cheap; 70B expensive | Varies; strong distills | Efficient at small sizes |
| **Scalability to Phase 9** | Good MoE path | Meta ecosystem | Strong research momentum | Google-dependent |

### Why Not Llama?

- Llama Community License imposes **deployment and scale restrictions** that may conflict with Phase 8 public release plans — legal review required per use case
- Arabic performance is acceptable but **not the primary design center** of Meta pretraining
- Strong ecosystem, but Qwen3 offers better **Arabic/cost balance** in the 30B MoE class for our roadmap

### Why Not DeepSeek?

- Excellent reasoning and code; **strong alternative** for Phase 6 comparisons
- License and export/compliance review needed for Saudi deployment context
- May be selected as **routing fallback** in future multi-model architecture (see `research/FUTURE_IDEAS.md`)
- Primary concern: **regional data moat** matters more than base reasoning — either base can be fine-tuned; Qwen selected for Arabic + MoE efficiency balance

### Why Not Gemma?

- Attractive for edge/small deployments
- **Weaker Arabic and regional knowledge** at comparable sizes
- Google Terms may constrain certain commercial redistribution patterns
- Better as a **future small-model distillation target** than Phase 1 base

---

## Licensing

### Repository Code

Apache 2.0 — see [LICENSE](../LICENSE)

### Qwen3-30B-A3B-Instruct Weights

- Governed by **Qwen Model License Agreement** (verify current version on Hugging Face at download time)
- Typically permits research and commercial use subject to acceptable use policy and attribution
- **Action required (Phase 4):** Legal review snapshot stored in `docs/legal/` (future) before public weight redistribution

### Fine-Tuned Derivatives (ArabArenaAI-1)

- Must comply with **base model license** plus **training data licenses**
- Most restrictive data license governs redistribution
- Model card must list base model, data mix summary, and license stack

---

## Arabic Performance Expectations

### Base Model (Phase 4 baseline)

Expected strengths:

- MSA comprehension and generation
- Bilingual Arabic–English technical Q&A
- General reasoning translated into Arabic output

Expected weaknesses (targets for Phase 5):

- Saudi-specific government process details
- Khaleeji dialect nuance
- Vision 2030 program specifics and recent policy updates
- Formal Saudi business correspondence conventions
- Hallucination on local entities and dates

### Post Fine-Tune (Phase 5 target)

- Measurable lift on **Saudi knowledge** and **Arabic reasoning** benchmarks (see [BENCHMARKS.md](BENCHMARKS.md))
- Preserve **programming** capability within agreed regression tolerance
- Document remaining failure modes honestly in model card

---

## Cost & Scalability

### Training (Phase 5 — LoRA estimate)

| Resource | Indicative planning assumption |
|----------|-------------------------------|
| Method | LoRA on attention + MLP (config TBD) |
| Hardware | 1–8× high-memory GPUs (A100/H100 class) |
| Duration | Days, not weeks, for first adapter (data-size dependent) |
| Storage | Adapters << full weights; artifact registry required |

Exact estimates deferred to Phase 5 experiment plans.

### Inference (Phase 7)

- MoE ~3B active params → lower per-token cost than dense 30B
- vLLM / TGI / custom serving — decision in Phase 7
- Batch API for partners; rate limits and audit logging mandatory

---

## Future Migration Path

```
┌──────────────────┐     ┌─────────────────────┐     ┌──────────────────────┐
│ Qwen3-30B-A3B    │────►│ ArabArenaAI-1 LoRA  │────►│ ArabArenaAI-1 Release│
│ (base instruct)  │     │ (regional SFT)      │     │ (private → public)   │
└──────────────────┘     └─────────────────────┘     └──────────────────────┘
           │                                                    │
           │              ┌─────────────────────┐               │
           └─────────────►│ Continued pretrain  │◄──────────────┘
                          │ on regional corpus  │
                          │ (Phase 9 option)    │
                          └──────────┬──────────┘
                                     ▼
                          ┌─────────────────────┐
                          │ ArabArenaAI-2       │
                          │ (independent FM path)│
                          └─────────────────────┘
```

### Migration Triggers (when to move beyond Qwen base)

1. **License friction** blocks Phase 8 public release goals
2. **Benchmark ceiling** — LoRA cannot close Saudi/GCC gap vs frontier APIs
3. **Data scale** — regional pretraining corpus large enough to justify custom train
4. **Architecture** — MoE/dense/context-length requirements outgrow Qwen constraints
5. **Strategic independence** — business requirement for fully owned model lineage

### Continuity Principles

- Maintain **benchmark regression suite** across any base migration
- Version adapters and checkpoints with immutable data snapshots
- Document **knowledge cutoff** and **regional update** process per release

---

## Model Artifacts Layout (future)

```
models/
├── base/                 # Reference to Qwen3 (not committed)
├── adapters/             # LoRA checkpoints (gitignored)
└── cards/                # Model cards per release
```

---

## Phase 4–5 Checklist

- [ ] Verify Qwen license snapshot and legal approval
- [ ] Download base weights to secure artifact store (not git)
- [ ] Run Phase 4 baseline on all benchmark categories
- [ ] Select LoRA hyperparameters from pilot experiments
- [ ] Publish internal model card for ArabArenaAI-1 v0.1

---

## Related Documents

- [DATA_STRATEGY.md](DATA_STRATEGY.md)
- [BENCHMARKS.md](BENCHMARKS.md)
- [../ROADMAP.md](../ROADMAP.md)
- [../research/FUTURE_IDEAS.md](../research/FUTURE_IDEAS.md)
