# Model Release Policy — ArabArenaAI-1

This policy defines **mandatory conditions** before ArabArenaAI-1 may be promoted to private (Phase 7) or public (Phase 8) release. No exceptions without written ADR and executive sign-off.

Related: [EVALUATION_FRAMEWORK.md](EVALUATION_FRAMEWORK.md) · [METRICS.md](METRICS.md) · [VISION.md](VISION.md)

---

## Policy Statement

**ArabArenaAI-1 cannot be released** (private or public) unless all **hard gates** in this document are satisfied simultaneously. Partial excellence does not compensate for failure on Saudi-first, Arabic-first, or safety metrics.

---

## Release Tiers

| Tier | Phase | Audience | Policy section |
|------|-------|----------|----------------|
| **Internal** | 5–6 | ML team, leadership | Hard gates + Phase 5 deltas |
| **Private** | 7 | Partners, pilots | Hard gates + CSAT |
| **Public** | 8 | General availability | Hard gates + transparency package |

---

## Hard Release Gates (all tiers)

The following **must all pass** on the **same checkpoint** using the frozen benchmark harness:

### 1. Arabic benchmark score

| Attribute | Requirement |
|-----------|-------------|
| Metric | `arabic_reasoning` category score |
| **Minimum** | **≥ 75 / 100** (public); **≥ 70 / 100** (private pilot) |
| Measurement | [arabic_reasoning.yaml](../evaluation/benchmarks/arabic_reasoning.yaml) |
| Rationale | Arabic-first — reasoning must be native, not translated |

### 2. Saudi knowledge score

| Attribute | Requirement |
|-----------|-------------|
| Metric | `saudi_knowledge` category score |
| **Minimum** | **≥ 80 / 100** (public); **≥ 75 / 100** (private pilot) |
| Measurement | [saudi_knowledge.yaml](../evaluation/benchmarks/saudi_knowledge.yaml) |
| Rationale | Saudi-first — primary differentiated value |
| Maintenance | Items past `valid_until` excluded until refreshed |

### 3. Programming score

| Attribute | Requirement |
|-----------|-------------|
| Metric | `programming` category Pass@1 score |
| **Minimum** | **≥ 90 / 100** (public); **≥ 85 / 100** (private pilot) |
| **Regression floor** | **≥ 95%** of Phase 4 Qwen3 baseline score (always) |
| Measurement | [programming.yaml](../evaluation/benchmarks/programming.yaml) |
| Rationale | Developer-friendly — fine-tune must not collapse code ability |

### 4. Hallucination rate

| Attribute | Requirement |
|-----------|-------------|
| Metric | Unsupported factual claims on **grounded** Saudi knowledge & summarization tasks |
| **Maximum (public)** | **≤ 5%** overall; **≤ 1% critical** (wrong gov entity, law, date) |
| **Maximum (private)** | **≤ 8%** overall; **≤ 2% critical** |
| Measurement | Grader rubric in [EVALUATION_FRAMEWORK.md](EVALUATION_FRAMEWORK.md) |
| Rationale | Trust — especially for government and business use |

---

## Additional Public Release Requirements (Phase 8 only)

Public release requires **hard gates above** plus:

| Requirement | Detail |
|-------------|--------|
| **Business knowledge** | **≥ 72 / 100** |
| **AAS composite** | **≥ 78 / 100** |
| **Model card** | Published with limitations, data mix summary, license stack |
| **Benchmark transparency** | Public summary of methodology and item counts |
| **Safety review** | Red-team report completed; no open critical findings |
| **Legal review** | Weight/API release approved; L2/L3 data stack cleared |
| **Support commitment** | Defined maintenance and update cadence for Saudi facts |

---

## Fine-Tune Promotion Requirements (Phase 5 → 6)

Before internal comparator runs, the fine-tuned checkpoint must show:

| Metric | Requirement |
|--------|-------------|
| Saudi knowledge Δ vs Phase 4 | **≥ +10 points** |
| Arabic reasoning Δ vs Phase 4 | **≥ +5 points** |
| Programming vs Phase 4 | **≥ 95%** of baseline |
| Hallucination vs Phase 4 | **Not worse by > 2 percentage points** |

Failure → **do not proceed** to Phase 6 marketing or Phase 7 pilots.

---

## Private Pilot Requirements (Phase 7)

| Metric | Requirement |
|--------|-------------|
| All hard gates | Private pilot thresholds (see above) |
| CSAT Arabic fluency | **≥ 4.0 / 5.0** |
| CSAT Saudi relevance | **≥ 4.0 / 5.0** |
| Minimum responses | **≥ 50** qualified pilot surveys |
| Security review | Completed |
| Acceptable use policy | Published to partners |

---

## Automatic Release Blocks

Release is **automatically blocked** if any of the following are true:

- Benchmark training **leakage** detected
- **Missing** Saudi or Arabic category eval on promoted checkpoint
- **Unapproved** dataset (manifest not `approved`) used in training mix
- **License stack** prohibits intended release mode (weights vs API-only)
- **Critical** safety failure in red-team suite
- `valid_until` expired on **> 10%** of Saudi knowledge items without re-review

---

## Waiver Process

Waivers require:

1. Written ADR with scope, duration, and risk acceptance
2. ML lead + legal + product sign-off
3. Public communication plan if user-facing impact
4. Expiry date and re-eval scheduled

**Non-waivable:** L4 data usage, benchmark leakage, missing legal approval for weight release.

---

## Roles & Accountability

| Role | Responsibility |
|------|----------------|
| **Eval lead** | Runs harness; publishes scores |
| **Data lead** | Confirms no leakage; manifest audit |
| **Legal** | License stack sign-off (Phase 8) |
| **Product** | CSAT and pilot gates (Phase 7) |
| **Executive sponsor** | Final public release approval |

---

## Review Cadence

| Event | Action |
|-------|--------|
| Every checkpoint | Full category eval |
| Monthly | Saudi item `valid_until` audit |
| Pre-release | Gate checklist sign-off (this document) |
| Post-release (30d) | CSAT and hallucination re-audit |

---

## Related Documents

- [EVALUATION_FRAMEWORK.md](EVALUATION_FRAMEWORK.md)
- [METRICS.md](METRICS.md)
- [BENCHMARKS.md](BENCHMARKS.md)
- [MODEL_STRATEGY.md](MODEL_STRATEGY.md)
- [../ROADMAP.md](../ROADMAP.md)
