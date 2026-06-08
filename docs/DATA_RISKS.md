# Data Risks — ArabArenaAI-1

Risk register for the ArabArenaAI-1 data program. Review **quarterly** and before each collection phase (A–E).

Scale: **Severity** and **Likelihood** — `Low` · `Medium` · `High` · `Critical`

Related: [DATA_ACQUISITION_PLAN.md](DATA_ACQUISITION_PLAN.md) · [LICENSING_GUIDE.md](LICENSING_GUIDE.md) · [DATA_MOAT_STRATEGY.md](DATA_MOAT_STRATEGY.md)

---

## Risk Summary Matrix

| Risk | Severity | Likelihood | Owner |
|------|----------|------------|-------|
| Licensing | Critical | Medium | Legal + Data |
| Copyright | Critical | Medium | Legal |
| Hallucination | High | High | Eval + ML |
| Bias | High | Medium | Data + Eval |
| Data poisoning | High | Low–Medium | Data + Security |
| Quality | High | High | Data eng |
| Privacy | Critical | Medium | Legal + Security |
| Regulatory | Critical | Medium | Legal |

---

## 1. Licensing Risks

**Description:** Training or releasing models on data without clear ML/redistribution rights; L3 sources used without approval; Qwen + data license stack conflict.

| | |
|--|--|
| **Severity** | **Critical** |
| **Likelihood** | **Medium** |
| **Mitigation** | L0–L4 framework; manifest before collect; legal snapshot in `docs/legal/licenses/`; L3 written approval; weight-release license stack review; no L4 ever |

---

## 2. Copyright Risks

**Description:** Ingesting news, books, or media without rights; CC BY-SA share-alike affecting derivatives; mixed OSS licenses in code corpora.

| | |
|--|--|
| **Severity** | **Critical** |
| **Likelihood** | **Medium** |
| **Mitigation** | Prefer government open data and L1; attribution NOTICE file for L2; per-repo license matrix for code; no news without L3 contract; legal review before Phase 8 |

---

## 3. Hallucination Risks

**Description:** Model confidently states false Saudi facts (ministries, dates, programs) learned from stale or noisy data.

| | |
|--|--|
| **Severity** | **High** |
| **Likelihood** | **High** |
| **Mitigation** | `source_ref` + `valid_until` on items; Tier 1 official sources; refresh cadence; Saudi benchmark gate; RAG with citations (future); hallucination rate ≤ 5% release policy |

---

## 4. Bias Risks

**Description:** Over-representation of dialect, region, gender, or ideology; stereotyping in business or cultural content; English-centric bias in code-heavy mix.

| | |
|--|--|
| **Severity** | **High** |
| **Likelihood** | **Medium** |
| **Mitigation** | Stratified mix audit; dialect labels; bias probes in eval (pre-Phase 8); human review samples; ADR-004 mix caps; document limitations in model card |

---

## 5. Data Poisoning Risks

**Description:** Adversarial or corrupted text in crawls, user submissions, or compromised partner feeds causes backdoors or systematic errors.

| | |
|--|--|
| **Severity** | **High** |
| **Likelihood** | **Low–Medium** (higher for web crawl) |
| **Mitigation** | No unreviewed crawl at scale; checksum manifests; anomaly detection on new shards; partner feed validation; defer Tier 3 crawls until Tier 1 pipeline mature; secrets/toxicity scanners |

---

## 6. Quality Risks

**Description:** OCR garbage, machine translation, spam, duplicates, and low-fluency Arabic dilute training signal.

| | |
|--|--|
| **Severity** | **High** |
| **Likelihood** | **High** |
| **Mitigation** | Quality score ≥ 0.65 gate; deduplication; language ID; reject < 0.50; quality over quantity principle; human audit ≥ 1% per source; Tier 3 last |

---

## 7. Privacy Risks

**Description:** PII in corpora (names, IDs, contact info); partner data leakage; cross-border transfer without PDPL compliance.

| | |
|--|--|
| **Severity** | **Critical** |
| **Likelihood** | **Medium** |
| **Mitigation** | PII scan before train; redaction pipeline; `pii_status` in manifests; partner isolated storage; PDPL review for L3; never collect patient/identity databases |

---

## 8. Regulatory Risks

**Description:** Violations of Saudi PDPL, export controls, sector rules (finance, telecom); training on data restricted for ML in ToS.

| | |
|--|--|
| **Severity** | **Critical** |
| **Likelihood** | **Medium** |
| **Mitigation** | Legal review Phase A–C; document jurisdiction per manifest; no scraping authenticated systems; sector-specific review for finance/health if added; compliance sign-off before public release |

---

## Cross-Cutting Controls

| Control | Phases |
|---------|--------|
| Manifest + legal gate | All |
| External storage only (ADR-002) | All |
| Benchmark holdout isolation | All |
| Quarterly risk review | Ongoing |
| Incident response for data breach | Phase 7+ |

---

## Escalation

| Trigger | Action |
|---------|--------|
| L4 source ingested by mistake | Halt train; delete snapshot; incident report |
| PII found in training shard | Quarantine shard; re-scan corpus |
| License challenge received | Pause release; legal + ADR |
| Poisoning suspected | Freeze mix; forensics on manifest chain |

---

## Related Documents

- [DATA_ACQUISITION_PLAN.md](DATA_ACQUISITION_PLAN.md)
- [DATA_PIPELINE.md](DATA_PIPELINE.md)
- [MODEL_RELEASE_POLICY.md](MODEL_RELEASE_POLICY.md)
