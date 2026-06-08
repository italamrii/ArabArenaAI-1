# Benchmark Strategy — ArabArenaAI-1

This document defines evaluation categories, methodology, and scoring for ArabArenaAI-1. Benchmarks are the **contract** between research, product, and release gates — especially for Saudi-first and Arabic-first claims.

---

## Principles

1. **Measure what we ship** — Categories map to real user scenarios, not academic trivia alone
2. **Arabic-native evaluation** — Prompts and gold answers in Arabic where the skill is Arabic
3. **Frozen holdouts** — Test sets never appear in training data (verified in Phase 3)
4. **Comparable baselines** — Same prompts, decoding params, and graders for all models in Phase 6
5. **Honest regression** — Fine-tuning must not collapse programming or safety without explicit acceptance

---

## Evaluation Pipeline (planned)

```
evaluation/benchmarks/     # Task definitions, prompts, gold labels
evaluation/reports/          # Scored runs (gitignored outputs)
scripts/                     # Harness CLI (Phase 4)
```

Each run records: model ID, checkpoint, prompt template version, temperature, seed, hardware, timestamp.

---

## Categories

### 1. Arabic Reasoning

**Purpose:** Measure logical and multi-step reasoning **in Arabic**, not merely translation from English.

| Sub-skill | Example task type |
|-----------|-------------------|
| Deduction | Syllogisms, constraint puzzles (Arabic prompt) |
| Multi-step | Word problems, planning scenarios |
| Ambiguity | Disambiguation in Arabic syntax |
| Counterfactual | "What if" scenarios in formal Arabic |

**Primary metric:** Accuracy vs gold answer (exact or rubric-graded)

**Secondary:** Reasoning completeness rubric (1–5)

---

### 2. Saudi Knowledge

**Purpose:** Factual and procedural knowledge specific to Saudi Arabia.

| Sub-domain | Examples |
|------------|----------|
| Vision 2030 | Programs, giga-projects (with date stamps) |
| Government services | Public-facing processes (from official sources) |
| Geography & admin | Regions, cities, institutions |
| Economy | Tadawul, major sectors, labor concepts (public info) |
| Culture | Holidays, customs, business etiquette |

**Primary metric:** Factual accuracy (binary per item + partial credit rubric)

**Critical:** Items must include `source_ref` and `valid_until` metadata for maintenance

---

### 3. Business Knowledge

**Purpose:** Entrepreneurship, startups, formal business Arabic, GCC commercial context.

| Sub-skill | Examples |
|-----------|----------|
| Terminology | Define and use business terms in Arabic |
| Scenarios | Market entry, pitch feedback, partnership clauses (simplified) |
| Documents | Summarize mock MOU excerpts |
| Regional | GCC trade concepts, free zones (public knowledge) |

**Primary metric:** Rubric score (correctness, register, actionability)

---

### 4. Programming

**Purpose:** Preserve and measure code generation and debugging (global priority #5).

| Sub-skill | Examples |
|-----------|----------|
| Code generation | Python, JS tasks with Arabic problem statements |
| Debugging | Find bug from Arabic-described spec |
| SQL / data | Query writing from Arabic requirements |
| Bilingual | Arabic comment + English code consistency |

**Primary metric:** Pass@1 on executable tests (HumanEval-style) or static analysis where execution unavailable

**Regression gate:** Phase 5 fine-tune must stay within **≥ 95%** of Phase 4 base programming score unless waived

---

### 5. Summarization

**Purpose:** Condense Arabic (and bilingual) documents faithfully.

| Variant | Input | Expected output |
|---------|-------|-----------------|
| News | Arabic article | 3–5 bullet summary |
| Business | Report excerpt | Executive summary in formal Arabic |
| Mixed | AR body + EN terms | Preserve terminology |

**Primary metric:** ROUGE-L (reference) + LLM-judge rubric (consistency, omission, hallucination)

**Hallucination penalty:** −1.0 per introduced factual claim not in source (judge rubric)

---

### 6. Translation

**Purpose:** Arabic ↔ English quality for business and technical content.

| Direction | Notes |
|-----------|-------|
| AR → EN | Formal and technical |
| EN → AR | MSA default; dialect only when specified |
| Bidirectional | Preserve numbers, entities, legal terms |

**Primary metric:** COMET or chrF++ (reference-based) + human spot-check sample

**Secondary:** Named entity preservation rate

---

### 7. Long-Context Understanding

**Purpose:** Retrieve and reason over long Arabic documents (policies, contracts, manuals).

| Parameter | Initial target |
|-----------|----------------|
| Context length | 32K tokens (scale to model max in Phase 4) |
| Task | Needle-in-haystack + multi-section QA |

**Primary metric:** Retrieval accuracy + answer correctness

**Setup:** Synthetic needles + real long documents (licensed)

---

## Scoring Methodology

### Per-Item Scoring

| Score type | When used |
|------------|-----------|
| **Binary (0/1)** | Closed QA with single gold answer |
| **Partial (0–1)** | Multi-fact answers; proportional credit |
| **Rubric (1–5)** | Open-ended generation (business, summarization) |
| **Pass@k** | Code tasks |

Normalized category score:

```
category_score = (sum of item scores / sum of max scores) × 100
```

Report as **percentage 0–100** per category.

### Aggregate ArabArena Score (AAS)

Weighted composite for headline tracking:

| Category | Weight |
|----------|--------|
| Arabic reasoning | 20% |
| Saudi knowledge | 25% |
| Business knowledge | 15% |
| Programming | 15% |
| Summarization | 10% |
| Translation | 10% |
| Long-context | 5% |

```
AAS = Σ (weight_i × category_score_i)
```

Weights reflect **Saudi-first / Arabic-first** priorities. Review annually.

### Phase 6 Comparison Protocol

For GPT, Claude, Gemini, DeepSeek:

- Identical prompt templates (Arabic primary)
- Fixed decoding: `temperature=0` where supported, else lowest stable setting
- Same grader (automated + frozen human subset)
- Report **AAS**, per-category scores, cost per 1K items, latency p50/p95
- Minimum **500 items** per major category before public claims (stretch goal)

---

## Quality Gates

### Phase 4 (Baseline)

- Complete all categories with ≥ 100 items each (initial minimum)
- Publish failure taxonomy (10+ recurring error types)

### Phase 5 (Post Fine-Tune)

- **Δ Saudi knowledge ≥ +10 points** vs Phase 4 base (initial target)
- **Δ Arabic reasoning ≥ +5 points**
- Programming regression within tolerance (see §4)

### Phase 6 (Internal Benchmark)

- Win or tie on Saudi + Arabic reasoning vs **≥ 2** comparators
- Document losses honestly with examples

### Phase 8 (Public Release)

- Public benchmark card with limitations and item counts
- Reproducibility package (prompts + grader version)

---

## Bias & Safety Evaluation (future extension)

Not primary categories in v0.1 but required before Phase 8:

- Stereotype and toxicity probes (Arabic)
- Refusal behavior on harmful requests
- Political sensitivity handling (neutral, sourced responses)

Track under separate **Safety** report — not blended into AAS.

---

## Benchmark Item Schema

```yaml
item_id: ara-sa-0001
category: saudi_knowledge
sub_domain: vision_2030
language: ar
difficulty: medium
prompt: |
  ...
gold_answer: |
  ...
rubric: null  # or path to rubric
source_ref: https://...
valid_until: 2027-01-01
license: L0
```

Store items under `evaluation/benchmarks/` by category in Phase 4.

---

## Related Documents

- [DATA_STRATEGY.md](DATA_STRATEGY.md) — holdout and leakage policy
- [MODEL_STRATEGY.md](MODEL_STRATEGY.md) — base vs fine-tuned comparisons
- [../ROADMAP.md](../ROADMAP.md) — Phases 4 and 6
