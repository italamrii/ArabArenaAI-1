# Evaluation Harness — ArabArenaAI-1

Phase 4 implementation guide for the ArabArenaAI-1 evaluation harness — a modular, provider-agnostic system for benchmarking models before training or data collection.

Related governance (not modified by harness code):

- [EVALUATION_FRAMEWORK.md](EVALUATION_FRAMEWORK.md) — release gates and pass/fail criteria  
- [MODEL_RELEASE_POLICY.md](MODEL_RELEASE_POLICY.md) — public/private release thresholds  
- [BENCHMARKS.md](BENCHMARKS.md) — benchmark strategy  

> **AAS weight note:** The executable AAS calculator in `evaluation/scorers/aas.py` uses Phase 4 harness weights (including **government** at 15%). Governance docs may reference a related composite for reporting; the harness module is the runtime source of truth for automated runs.

---

## Architecture

```
evaluation/
├── benchmarks/          # Legacy YAML item banks (150 seed questions)
├── datasets/            # JSONL benchmarks + loaders
├── registry/            # Pydantic schema + BenchmarkRegistry
├── runners/             # Provider adapters (OpenAI, Anthropic, …)
├── scorers/             # Rubric scoring + AAS calculator
├── results/             # JSON run artifacts (gitignored)
├── reports/             # Leaderboard + regression outputs (gitignored)
├── prompts/             # Default system prompt template
├── pipeline.py          # Orchestration (load → run → score → persist)
├── evaluate.py          # CLI entrypoint
└── dashboard.py         # Streamlit baseline dashboard (Phase 4.5)
```

### Clean Architecture layers

| Layer | Responsibility |
|-------|----------------|
| **Registry / datasets** | Load & validate benchmark definitions |
| **Runners** | Model inference abstraction (no scoring logic) |
| **Scorers** | Deterministic rubric + AAS (no provider code) |
| **Results / reports** | Persistence, leaderboard, regression |
| **Pipeline / CLI** | Composition and observability |

Dependencies point inward: CLI → pipeline → registry/runners/scorers → storage.

---

## Evaluation Flow

```
1. Load benchmarks (JSONL + optional YAML)
2. Validate schema / dedupe IDs
3. Select runner by --model
4. For each item:
     prompt → runner.generate() → score_response()
5. Aggregate category scores (weighted)
6. Compute AAS
7. Save evaluation/results/{run_id}.json
8. Update evaluation/reports/leaderboard.json
9. Compare prior run → regression JSON + Markdown
```

---

## Benchmark Lifecycle

| Stage | Location | Status |
|-------|----------|--------|
| Author | `evaluation/datasets/*.jsonl` or `evaluation/benchmarks/*.yaml` | PR review |
| Register | `BenchmarkRegistry.load()` | Schema validated |
| Freeze | Git tag + `benchmark_version` | Holdout for training ban |
| Run | `evaluate.py` | Scored + stored |
| Maintain | Update `valid_until` on Saudi items | Legal/data review |

**Rules:**

- Benchmark text must never enter training mix (see [DATA_MOAT_STRATEGY.md](DATA_MOAT_STRATEGY.md))  
- JSONL is the standardized interchange format; YAML remains supported for legacy seed banks  
- JSONL takes precedence on duplicate IDs  

---

## Benchmark Schema

Each item (JSONL or normalized YAML):

| Field | Required | Description |
|-------|----------|-------------|
| `id` | yes | Unique identifier |
| `category` | yes | See categories below |
| `difficulty` | no | `easy` / `medium` / `hard` |
| `weight` | no | Category aggregation weight (default 1.0) |
| `question` | yes | Prompt text |
| `reference_answer` | yes | Gold reference |

### Categories

| Category key | Description |
|--------------|-------------|
| `saudi_knowledge` | Saudi facts, culture, economy |
| `arabic_reasoning` | Arabic logical / arithmetic reasoning |
| `business` | Entrepreneurship, formal business Arabic |
| `government` | Government services, Vision 2030 programs, Nitaqat |
| `programming` | Code generation (Python, Java, JS, SQL, APIs) |
| `translation` | Arabic ↔ English |
| `summarization` | Condense Arabic passages |

Add new categories by extending `BenchmarkCategory` enum — no registry refactor required.

---

## Adding New Models

1. Create `evaluation/runners/{provider}_runner.py` implementing `BaseRunner`  
2. Register in `evaluation/runners/runner_factory.py`  
3. Document env vars in `.env.example`  
4. Run: `python evaluation/evaluate.py --model {provider}`  

**Implemented providers:**

| Key | Env vars |
|-----|----------|
| `mock` | none (tests / offline) |
| `openai` | `OPENAI_API_KEY`, optional `OPENAI_MODEL` |
| `anthropic` | `ANTHROPIC_API_KEY`, optional `ANTHROPIC_MODEL` |
| `google` | `GOOGLE_API_KEY`, optional `GOOGLE_MODEL` |
| `deepseek` | `DEEPSEEK_API_KEY`, optional `DEEPSEEK_MODEL` |
| `qwen` | Ollama local API (`qwen3:8b` default; set `QWEN_MODEL` or `--model-name`) |
| `llama` | placeholder — local inference Phase 4+ |

---

## Adding New Benchmarks

### JSONL (preferred)

Add a line to `evaluation/datasets/starter_benchmarks.jsonl` or create a new file and register in `evaluation/config.py`:

```json
{"id":"unique-id","category":"government","difficulty":"medium","weight":1.0,"question":"...","reference_answer":"..."}
```

Validate:

```bash
python -c "from evaluation.datasets.jsonl_loader import load_benchmarks; print(load_benchmarks('evaluation/datasets/starter_benchmarks.jsonl'))"
```

### YAML (legacy)

Continue using `evaluation/benchmarks/{name}.yaml` with `sample_questions`. Government-tagged items use `sub_domain: government_services`.

---

## Running Evaluations

### Install

```bash
pip install -r requirements-eval.txt
```

### Mock (no API keys)

```bash
python evaluation/evaluate.py --model mock --jsonl-only --limit 10
```

### Provider examples

```bash
python evaluation/evaluate.py --model openai
python evaluation/evaluate.py --model anthropic
python evaluation/evaluate.py --model deepseek
python evaluation/evaluate.py --model google --category saudi_knowledge
python evaluation/evaluate.py --model qwen --limit 10
python evaluation/evaluate.py --model qwen --model-name qwen3:14b
```

Requires [Ollama](https://ollama.com/) running locally with the model pulled (`ollama pull qwen3:8b`). Configure via `OLLAMA_BASE_URL`, `QWEN_MODEL`, `OLLAMA_TIMEOUT`.

### Flags

| Flag | Description |
|------|-------------|
| `--jsonl-only` | Skip YAML benchmark bank |
| `--limit N` | Run first N items only |
| `--category` | Filter single category |
| `--baseline-run ID` | Regression vs specific run |
| `--skip-leaderboard` | Skip leaderboard update |
| `--skip-regression` | Skip regression report |

---

## Understanding AAS

**ArabArena Score (AAS)** — weighted composite of category scores (0–100):

| Category | Weight |
|----------|--------|
| Saudi knowledge | 30% |
| Arabic reasoning | 20% |
| Business | 15% |
| Government | 15% |
| Programming | 10% |
| Translation | 5% |
| Summarization | 5% |

```python
from evaluation.scorers.aas import compute_aas
from evaluation.registry.benchmark_schema import BenchmarkCategory

result = compute_aas({BenchmarkCategory.SAUDI_KNOWLEDGE: 80.0, ...})
print(result.aas, result.weighted_contributions)
```

Missing categories score 0 and appear in `missing_categories`.

---

## Scoring Engine

Each response receives rubric scores **0–5**:

| Dimension | Meaning |
|-----------|---------|
| `accuracy` | Token overlap vs reference |
| `completeness` | Coverage relative to reference length |
| `relevance` | Overlap + non-empty response signal |

Programming items add keyword-aware scoring. Future LLM-as-judge can wrap `score_response()` without changing the pipeline.

Category score = weighted average of normalized rubric totals (0–100).

---

## Regression Detection

Compares two runs (default: previous vs current):

- Category drop beyond **5.0** points → regressed  
- AAS drop beyond **5.0** points → AAS regressed  

Outputs:

- `evaluation/reports/regression_{run_id}.json`  
- `evaluation/reports/regression_{run_id}.md`  

```python
from evaluation.reports.regression_detector import detect_regressions
from evaluation.results.storage import load_run

report = detect_regressions(load_run("baseline-id"), load_run("current-id"))
```

---

## Leaderboard

`evaluation/reports/leaderboard.json` — sorted by best AAS per `provider:model`, includes trend of last 10 runs.

Regenerated after each evaluation unless `--skip-leaderboard`.

---

## Result Storage

Each run → `evaluation/results/{run_id}.json`:

```json
{
  "run_id": "...",
  "timestamp": "ISO-8601",
  "model": "gpt-4o-mini",
  "provider": "openai",
  "category_scores": {"saudi_knowledge": 72.5},
  "aas": 68.4,
  "benchmark_count": 164,
  "execution_time": 42.1,
  "item_scores": [...],
  "traces": [
    {
      "benchmark_id": "sk-001",
      "category": "saudi_knowledge",
      "question": "...",
      "reference_answer": "...",
      "model_answer": "...",
      "accuracy": 2.5,
      "completeness": 4.0,
      "relevance": 3.0
    }
  ],
  "metadata": {...}
}
```

Legacy runs without `traces` remain loadable; scores are mapped from `item_scores` without question/answer text.

Query helpers: `list_runs()`, `load_run()`, `query_runs()` in `evaluation/results/storage.py`.

---

## Baseline Dashboard (Phase 4.5)

Local Streamlit dashboard for runs, leaderboard, and regression reports.

```bash
streamlit run evaluation/dashboard.py
```

Reads:

- `evaluation/reports/leaderboard.json`
- `evaluation/results/*.json`
- `evaluation/reports/regression_*.md`

Sections: Overview · Leaderboard · Model Details · Category Scores · Regression Reports · Raw Run JSON Viewer.

Sidebar filters: model · date/run · category.

---

## Testing

```bash
pip install -r requirements-eval.txt
pytest
```

Tests cover registry, JSONL loader, scoring, AAS, regression, leaderboard, pipeline integration, and dashboard data helpers.

---

## Observability

Structured logs via `arabarena.eval.*` loggers:

```
level=INFO logger=arabarena.eval.pipeline message=Evaluation complete run_id=... aas=... benchmark_count=...
```

---

## Related Documents

- [../evaluation/README.md](../evaluation/README.md)  
- [METRICS.md](METRICS.md)  
- [DATA_PIPELINE.md](DATA_PIPELINE.md)  
