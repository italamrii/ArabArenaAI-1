# Metrics & KPIs — ArabArenaAI-1

This document defines **future key performance indicators** for ArabArenaAI-1. Values are **targets to be calibrated** in Phase 4 (baseline) and Phase 6 (comparison). No scores exist yet — this is the measurement contract.

For benchmark categories and scoring math, see [BENCHMARKS.md](BENCHMARKS.md). For release gates, see [ROADMAP.md](../ROADMAP.md).

---

## Measurement Principles

1. **Report honestly** — publish limitations alongside headline numbers
2. **Same harness for all models** — Phase 6 comparators use identical prompts and graders
3. **Version everything** — model ID, adapter hash, prompt template version, benchmark version
4. **Separate automatic and human metrics** — automation scales; human eval validates trust
5. **Primary vs secondary** — Saudi and Arabic metrics gate release; others guard against regression

---

## KPI Definitions

### 1. Arabic Benchmark Score

| Attribute | Definition |
|-----------|------------|
| **What** | Composite score on **Arabic reasoning** benchmark category |
| **Scale** | 0–100 (normalized per [BENCHMARKS.md](BENCHMARKS.md)) |
| **Formula** | `category_score` for Arabic reasoning items |
| **Data source** | `evaluation/reports/` — automated grading on frozen holdout set |
| **Frequency** | Every model checkpoint; mandatory pre-release |
| **Owner** | Evaluation team |

| Milestone | Target (initial) |
|-----------|------------------|
| Phase 4 baseline (Qwen3 base) | Record only — establishes floor |
| Phase 5 post fine-tune | **≥ +5 points** vs Phase 4 baseline |
| Phase 6 vs comparators | **Win or tie** vs ≥ 2 frontier/open models |
| Phase 8 public release | **≥ 75** (recalibrate after Phase 4 baseline) |

---

### 2. Saudi Knowledge Score

| Attribute | Definition |
|-----------|------------|
| **What** | Accuracy on **Saudi knowledge** items (Vision 2030, gov services, geography, economy, culture) |
| **Scale** | 0–100 |
| **Formula** | Weighted accuracy + partial credit per item rubric |
| **Data source** | Frozen Saudi holdout; each item has `source_ref` and `valid_until` |
| **Frequency** | Every checkpoint; **monthly refresh** of time-sensitive item audit |
| **Owner** | Evaluation + domain reviewers |

| Milestone | Target (initial) |
|-----------|------------------|
| Phase 4 baseline | Record only |
| Phase 5 post fine-tune | **≥ +10 points** vs Phase 4 baseline |
| Phase 6 vs comparators | **Strict win** on Saudi category vs all comparators (stretch) or **top-2** (minimum) |
| Phase 8 public release | **≥ 80** (recalibrate after item bank ≥ 500 questions) |

**Alert threshold:** Any **> 5 point** drop vs previous checkpoint triggers training post-mortem before further promotion.

---

### 3. Programming Score

| Attribute | Definition |
|-----------|------------|
| **What** | Code generation and debugging capability (Python, JS, SQL; Arabic problem statements supported) |
| **Scale** | 0–100 (Pass@1 normalized) |
| **Formula** | Executable test pass rate on benchmark suite |
| **Data source** | `evaluation/benchmarks/` programming subset |
| **Frequency** | Every checkpoint |
| **Owner** | Evaluation team |

| Milestone | Target (initial) |
|-----------|------------------|
| Phase 4 baseline | Record only — **regression reference** |
| Phase 5 post fine-tune | **≥ 95%** of Phase 4 baseline score |
| Phase 6 | No requirement to beat GPT/DeepSeek; **must not collapse** |
| Phase 8 | **≥ 90** absolute (recalibrate after harness built) |

---

### 4. User Satisfaction

| Attribute | Definition |
|-----------|------------|
| **What** | Structured satisfaction from pilot and partner users |
| **Scale** | 1–5 Likert (CSAT); optional NPS for Phase 7+ |
| **Dimensions** | Arabic fluency · Saudi relevance · usefulness · trust · latency |
| **Data source** | In-product surveys, partner feedback forms, annotated session samples |
| **Frequency** | Weekly during Phase 7 pilot; monthly post-launch |
| **Owner** | Product + partnerships |

| Milestone | Target (initial) |
|-----------|------------------|
| Phase 7 private pilot | **CSAT ≥ 4.0/5.0** on Arabic fluency and Saudi relevance |
| Phase 8 public (30 days) | **CSAT ≥ 4.2/5.0** overall; **≥ 4.0** on trust |
| Phase 8 (90 days) | **NPS ≥ +30** among active developer users (if measured) |

**Minimum sample:** ≥ 50 qualified responses per reporting period before publishing internally.

---

### 5. Hallucination Rate

| Attribute | Definition |
|-----------|------------|
| **What** | Fraction of responses containing **unsupported factual claims** on grounded tasks |
| **Scale** | 0–100% (lower is better) |
| **Formula** | `(hallucinated items / graded items) × 100` |
| **Grading** | Automated judge + human audit on stratified sample (≥ 10% of items) |
| **Task types** | Saudi knowledge QA, summarization (claim not in source), business scenarios |
| **Data source** | Evaluation harness + pilot session audits |
| **Frequency** | Every checkpoint (eval); continuous sample during Phase 7+ |
| **Owner** | Evaluation + safety review |

| Milestone | Target (initial) |
|-----------|------------------|
| Phase 4 baseline | Record only |
| Phase 5 post fine-tune | **≤ baseline + 2pp** (must not worsen materially) |
| Phase 7 pilot | **≤ 8%** on Saudi knowledge grounded set |
| Phase 8 public | **≤ 5%** on Saudi knowledge; **≤ 10%** on summarization |

**Severity classes:** Critical (wrong gov entity/program) · Major (wrong date/statistic) · Minor (imprecise phrasing). Critical hallucination rate must be **≤ 1%** at Phase 8.

---

### 6. Response Quality Score

| Attribute | Definition |
|-----------|------------|
| **What** | Holistic generation quality on open-ended tasks (business, dialogue, mixed technical) |
| **Scale** | 1–5 rubric → normalized to 0–100 |
| **Dimensions** | Correctness · completeness · register (MSA/dialect) · structure · actionability |
| **Formula** | Mean rubric score / 5 × 100 |
| **Data source** | LLM-judge (frozen prompt) + monthly human calibration batch |
| **Frequency** | Every checkpoint; human calibration monthly |
| **Owner** | Evaluation team |

| Milestone | Target (initial) |
|-----------|------------------|
| Phase 4 baseline | Record only |
| Phase 5 post fine-tune | **≥ +8 points** on business + summarization subsets |
| Phase 6 | **≥ competitor mean** on combined open-ended subset |
| Phase 8 | **≥ 82** overall; **≥ 85** on business knowledge category |

**Calibration rule:** When LLM-judge diverges from human panel by **> 0.3** on 1–5 scale, retrain judge prompts before next report.

---

## Composite: ArabArena Score (AAS)

Headline internal metric — weighted composite from [BENCHMARKS.md](BENCHMARKS.md):

| Category | Weight |
|----------|--------|
| Arabic reasoning | 20% |
| Saudi knowledge | 25% |
| Business knowledge | 15% |
| Programming | 15% |
| Summarization | 10% |
| Translation | 10% |
| Long-context | 5% |

Report **AAS** alongside every individual KPI. Do not optimize AAS alone at the expense of Saudi knowledge or hallucination rate.

---

## Dashboard & Reporting (future)

| Report | Audience | Phase |
|--------|----------|-------|
| Baseline card | Internal | Phase 4 |
| Fine-tune delta report | ML + leadership | Phase 5 |
| Comparator scorecard | Leadership + partners | Phase 6 |
| Public benchmark card | External | Phase 8 |
| Pilot CSAT / hallucination weekly | Product | Phase 7 |

Store generated reports under `evaluation/reports/` (external/gitignored). Commit **summary markdown** to `docs/reports/` when public transparency requires it (Phase 8).

---

## KPI ↔ Release Gate Matrix

| Gate | Required KPIs |
|------|---------------|
| Phase 5 → 6 | Arabic + Saudi Δ vs baseline; programming regression pass; hallucination not worse |
| Phase 6 → 7 | Saudi + Arabic vs comparators; response quality ≥ competitor mean |
| Phase 7 → 8 | CSAT ≥ 4.2; hallucination ≤ 5% Saudi; critical hallucination ≤ 1% |
| Phase 8 public | All Phase 8 targets met; public benchmark card published |

---

## Related Documents

- [BENCHMARKS.md](BENCHMARKS.md) — category definitions and scoring
- [VISION.md](VISION.md) — success and failure definitions
- [DECISIONS.md](DECISIONS.md) — ADRs affecting metric changes
- [../ROADMAP.md](../ROADMAP.md) — phase timeline
