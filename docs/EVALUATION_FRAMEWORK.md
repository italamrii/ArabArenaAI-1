# Evaluation Framework — ArabArenaAI-1

This document defines **pass/fail criteria**, **minimum release scores**, and **benchmark weighting** for ArabArenaAI-1 evaluation. It operationalizes [BENCHMARKS.md](BENCHMARKS.md) and [METRICS.md](METRICS.md) for Phase 4+ runs.

**Status:** Benchmark item bank v0.1 (150 seed questions). Targets calibrate after Phase 4 baseline.

---

## Scope

| In scope | Out of scope (separate reports) |
|----------|----------------------------------|
| Automated benchmark harness scores | Ad-hoc chat demos |
| Frozen holdout in `evaluation/benchmarks/` | Training data QA |
| Phase 4–8 release gates | Red-team safety suite (pre-Phase 8) |

---

## Benchmark Inventory (v0.1)

| File | Category | Items | Primary metric |
|------|----------|-------|----------------|
| `saudi_knowledge.yaml` | Saudi knowledge | 25 | Accuracy 0–100 |
| `arabic_reasoning.yaml` | Arabic reasoning | 25 | Accuracy 0–100 |
| `business_knowledge.yaml` | Business knowledge | 25 | Rubric 0–100 |
| `programming.yaml` | Programming | 25 | Pass@1 0–100 |
| `translation.yaml` | Translation | 25 | chrF++ / entity preservation |
| `summarization.yaml` | Summarization | 25 | ROUGE-L + hallucination rubric |

**Total seed questions:** 150 (expand to ≥500 per major category before Phase 8 public claims).

---

## Scoring Model

### Per-category score

```
category_score = (sum of item_scores / max_possible) × 100
```

### ArabArena Score (AAS) — weighted composite

| Category | Weight | Rationale |
|----------|--------|-----------|
| Saudi knowledge | **25%** | Saudi-first primary gate |
| Arabic reasoning | **20%** | Arabic-first reasoning |
| Business knowledge | **15%** | Business-aware mission |
| Programming | **15%** | Engineering regression guard |
| Summarization | **10%** | Document workflows |
| Translation | **10%** | Bilingual business |
| Long-context | **5%** | *(Category added Phase 4+; weight reserved)* |

```
AAS = Σ (weight_i × category_score_i)
```

> Until long-context items exist, redistribute its 5% proportionally across Saudi (+2), Arabic (+2), Business (+1) for internal reporting only — document in run metadata.

---

## Pass Criteria

A model **checkpoint passes** internal promotion when **all** applicable gates below are met for its target phase.

### Phase 4 — Baseline (record only)

| Gate | Pass criterion |
|------|----------------|
| Harness | All 6 categories run without error |
| Reproducibility | Same score ±0.5 pts on repeat run (same seed) |
| Documentation | Baseline report stored with model ID and prompt version |

*No minimum score required — establishes floor.*

### Phase 5 — Post fine-tune (internal promotion)

| Gate | Pass criterion |
|------|----------------|
| Saudi knowledge Δ | **≥ +10 points** vs Phase 4 baseline |
| Arabic reasoning Δ | **≥ +5 points** vs Phase 4 baseline |
| Programming regression | **≥ 95%** of Phase 4 baseline score |
| Hallucination (Saudi grounded) | **Not worse** than baseline + 2pp |
| Business knowledge Δ | **≥ +5 points** vs baseline (recommended) |

### Phase 6 — Comparator readiness

| Gate | Pass criterion |
|------|----------------|
| Saudi knowledge | Top-2 vs GPT, Claude, Gemini, DeepSeek (same harness) |
| Arabic reasoning | Win or tie vs **≥ 2** comparators |
| Programming | **≥ 95%** of Phase 4 baseline |
| Response quality (open-ended) | **≥ competitor mean** on business subset |

### Phase 7 — Private pilot release

| Gate | Pass criterion |
|------|----------------|
| All Phase 6 gates | Still met |
| CSAT (Arabic fluency + Saudi relevance) | **≥ 4.0 / 5.0** (≥50 responses) |
| Critical hallucination (Saudi) | **≤ 2%** on grounded audit set |

### Phase 8 — Public release

See [MODEL_RELEASE_POLICY.md](MODEL_RELEASE_POLICY.md) for hard minimums.

---

## Fail Criteria

A checkpoint **fails** promotion if **any** condition holds:

| Fail condition | Action |
|----------------|--------|
| Saudi knowledge **drops > 5 pts** vs previous promoted checkpoint | Block promotion; post-mortem |
| Programming **< 90%** of Phase 4 baseline (Phase 5+) | Block unless ADR waiver |
| Hallucination **> 10%** on Saudi grounded set | Block all external release |
| **Critical** Saudi factual error rate **> 1%** | Block public release |
| Benchmark **leakage detected** (item in training mix) | Invalidate run; re-split data |
| Harness **version mismatch** without re-baseline | Invalidate comparison |
| Eval run missing **required category** | Incomplete — fail |

---

## Minimum Release Scores (Phase 8 public)

Absolute floors — in addition to pass criteria above:

| Metric | Minimum | Scale |
|--------|---------|-------|
| **Arabic reasoning score** | **≥ 75** | 0–100 |
| **Saudi knowledge score** | **≥ 80** | 0–100 |
| **Programming score** | **≥ 90** | 0–100 |
| **Hallucination rate** (Saudi grounded) | **≤ 5%** | lower better |
| **Critical hallucination rate** (Saudi) | **≤ 1%** | lower better |
| **Business knowledge score** | **≥ 72** | 0–100 |
| **Translation score** | **≥ 70** | 0–100 |
| **Summarization score** | **≥ 70** | 0–100 |
| **AAS (composite)** | **≥ 78** | 0–100 |

These floors **recalibrate** after Phase 4 baseline if Qwen3 base already exceeds or falls far below them — change requires new ADR.

---

## Evaluation Workflow

```
┌─────────────────┐
│ Load benchmark  │  evaluation/benchmarks/*.yaml
│ YAML (frozen)   │
└────────┬────────┘
         ▼
┌─────────────────┐
│ Select model    │  base or adapter; record checkpoint hash
│ + decode params │  temperature=0 (or lowest stable)
└────────┬────────┘
         ▼
┌─────────────────┐
│ Run harness     │  Phase 4 implementation in scripts/
│ (per category)  │
└────────┬────────┘
         ▼
┌─────────────────┐
│ Grade outputs   │  auto + human calibration sample ≥10%
└────────┬────────┘
         ▼
┌─────────────────┐
│ Compute scores  │  category + AAS + hallucination
└────────┬────────┘
         ▼
┌─────────────────┐
│ Gate check      │  pass/fail vs phase table
└────────┬────────┘
         ▼
┌─────────────────┐
│ Publish report  │  evaluation/reports/ (gitignored)
└─────────────────┘
```

### Required run metadata

- `benchmark_version`, `harness_version`, `prompt_template_version`
- `model_id`, `adapter_hash`, `base_model`
- `timestamp`, `hardware`, `seed`, `temperature`
- `git_commit` of benchmark YAML

### Human review

- **10% stratified sample** per category each major run
- Monthly calibration for LLM-as-judge prompts (summarization, business)
- Saudi knowledge items with expired `valid_until` quarantined until updated

---

## Regression Policy

| Category | Policy |
|----------|--------|
| Saudi knowledge | Never regress > 5 pts vs last promoted |
| Arabic reasoning | Never regress > 5 pts vs last promoted |
| Programming | Never below 90% of Phase 4 baseline at public release |
| Hallucination | Monotonic improvement target; never worsen > 2pp vs baseline post fine-tune |

---

## Related Documents

- [BENCHMARKS.md](BENCHMARKS.md)
- [METRICS.md](METRICS.md)
- [MODEL_RELEASE_POLICY.md](MODEL_RELEASE_POLICY.md)
- [../evaluation/benchmarks/](../evaluation/benchmarks/)
- [DECISIONS.md](DECISIONS.md)
