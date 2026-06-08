# Data Targets — ArabArenaAI-1 (12-Month Horizon)

Quantitative targets for the **first 12 months** of the data program, starting from Phase 2 collection (post-strategy). Assumes Tier 1-first execution per [DATA_ACQUISITION_PLAN.md](DATA_ACQUISITION_PLAN.md) and ADR-004 mix policy.

**Note:** Token estimates are **planning ranges** — recalibrate after Phase A pilot ingest and tokenizer choice (Qwen3).

---

## Target Summary

| Metric | Minimum | Recommended | Stretch |
|--------|---------|-------------|---------|
| **Datasets (manifests collected)** | 8 | 14 | 20 |
| **Documents (processed)** | 150 K | 400 K | 1 M |
| **Tokens (processed, est.)** | 300 M | 800 M | 2 B |
| **Saudi content %** | 35% | **45%** | 55% |
| **Arabic content %** | 70% | **80%** | 88% |
| **Business content %** | 12% | **18%** | 25% |
| **Programming content %** | 5% | **8%** | 12% |

---

## 1. Number of Datasets

| Tier | Minimum | Recommended | Stretch |
|------|---------|-------------|---------|
| Tier 1 manifests `collected` | 4 | **7** | 7 |
| Tier 2 manifests `collected` | 2 | **5** | 7 |
| Tier 3 manifests `collected` | 0 | 2 | 6 |
| **Total collected** | **8** | **14** | **20** |

**Definitions:**

- **Collected** = raw snapshot stored externally + manifest updated (not merely `proposed`)  
- Tier 1 complete = all 7 Tier-1 sources at recommended  

---

## 2. Number of Documents

| | Minimum | Recommended | Stretch |
|--|---------|-------------|---------|
| **Processed documents** | 150,000 | **400,000** | 1,000,000 |

**Document** = one logical unit after cleaning (article, PDF section, page, Q&A pair, code file) — defined in Phase 3 cleaning spec.

| Source type | Recommended share |
|-------------|-------------------|
| Gov / policy PDFs & pages | 25% |
| Business / regulatory | 20% |
| Arabic general (Wiki, academic) | 30% |
| Dialect / dialogue | 5% |
| Code / technical | 8% |
| Translation pairs | 12% |

---

## 3. Number of Tokens

| | Minimum | Recommended | Stretch |
|--|---------|-------------|---------|
| **Processed tokens (est.)** | 300 M | **800 M** | 2 B |

**Estimation method:** Sum of UTF-8 chars ÷ 3.5 (Arabic-heavy heuristic) until official tokenizer audit in Phase 3.

| Guardrail | Value |
|-----------|-------|
| Max single-source share | ≤ 25% of tokens |
| Tier 3 web crawl share | ≤ 10% at recommended target |
| Min Saudi-token share | ≥ 35% minimum target |

---

## 4. Saudi Content %

| | Minimum | Recommended | Stretch |
|--|---------|-------------|---------|
| **Saudi-weighted tokens** | **35%** | **45%** | **55%** |

**Measurement:** Tokens tagged `country: SA` or Saudi-specific gov/business sources per manifest — not merely Arabic language.

**Alignment:** ADR-004 target ~40% Saudi in **training mix**; recommended 45% allows headroom after cleaning losses.

---

## 5. Arabic Content %

| | Minimum | Recommended | Stretch |
|--|---------|-------------|---------|
| **Arabic tokens** | **70%** | **80%** | **88%** |

Includes MSA, dialect (tagged), and mixed Arabic–English where Arabic dominates. Excludes pure English code comments-only files unless tagged technical.

---

## 6. Business Content %

| | Minimum | Recommended | Stretch |
|--|---------|-------------|---------|
| **Business-domain tokens** | **12%** | **18%** | **25%** |

Domains: `business`, `investment`, `regulatory`, `finance`, `entrepreneurship`, `procurement` per manifest `domain` field.

---

## 7. Programming Content %

| | Minimum | Recommended | Stretch |
|--|---------|-------------|---------|
| **Programming-domain tokens** | **5%** | **8%** | **12%** |

**Cap rationale:** Preserve programming benchmark (≥ 95% baseline) without diluting Saudi moat. Stretch only if Phase 4 baseline programming margin > 10 pts.

---

## Milestone Mapping (12 Months)

| Month | Milestone | Cumulative target (recommended) |
|-------|-----------|----------------------------------|
| M1–M2 | Phase A complete | 4 datasets, 80 M tokens, 50% Saudi of ingested |
| M3–M4 | Phase B complete | 7 datasets, 250 M tokens, 45% Saudi overall |
| M5–M7 | Phase C complete | 12 datasets, 500 M tokens, 18% business |
| M8–M9 | Phase D complete | 14 datasets, 700 M tokens, 8% programming |
| M10–M12 | Phase E selective | 14–20 datasets, **800 M–2 B** tokens, all mix gates |

---

## Success Gates (12-Month)

All **recommended** targets met **or** documented ADR waiver with compensating benchmark gains:

- [ ] ≥ 7 Tier-1 datasets collected and processed  
- [ ] Saudi content ≥ 45% processed tokens  
- [ ] Arabic content ≥ 80%  
- [ ] Mean quality score ≥ 0.65 corpus-wide  
- [ ] Zero critical PII findings in audit sample  
- [ ] 100% collected manifests have license snapshot  
- [ ] Benchmark holdout leakage check passed  

---

## When Targets Fail

| Miss | Response |
|------|----------|
| Saudi % < minimum | Pause Tier 2/3; accelerate Tier 1 |
| Quality < 0.65 mean | Tighten filters; reject sources |
| Programming over-cap | Trim code shards |
| Dataset count behind | Prioritize by Priority formula — do not bulk crawl |

---

## Related Documents

- [DATA_ACQUISITION_PLAN.md](DATA_ACQUISITION_PLAN.md)
- [DATA_STRATEGY.md](DATA_STRATEGY.md)
- [METRICS.md](METRICS.md)
- [ROADMAP.md](../ROADMAP.md)
