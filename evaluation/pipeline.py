"""Evaluation pipeline orchestration."""

from __future__ import annotations

import time
from datetime import datetime, timezone
from pathlib import Path

from evaluation.config import PROMPTS_DIR
from evaluation.logging_config import get_logger
from evaluation.registry.benchmark_registry import BenchmarkRegistry
from evaluation.registry.benchmark_schema import BenchmarkCategory
from evaluation.results.storage import EvaluationRunResult, EvaluationTraceItem, new_run_id, save_run
from evaluation.runners.base_runner import BaseRunner, RunnerError
from evaluation.runners.runner_factory import create_runner
from evaluation.scorers.aas import compute_aas
from evaluation.scorers.rubric import RubricScore, ScoringMode, aggregate_category_score, score_response

logger = get_logger("pipeline")


def load_system_prompt() -> str:
    prompt_path = PROMPTS_DIR / "default_prompt.txt"
    if prompt_path.exists():
        return prompt_path.read_text(encoding="utf-8").strip()
    return "You are a helpful assistant."


def run_evaluation(
    model: str,
    *,
    runner: BaseRunner | None = None,
    include_yaml: bool = True,
    limit: int | None = None,
    category_filter: BenchmarkCategory | None = None,
    scoring_mode: ScoringMode | str = ScoringMode.LEGACY,
) -> EvaluationRunResult:
    """Execute full evaluation pipeline."""
    start = time.perf_counter()
    registry = BenchmarkRegistry()
    report = registry.load(include_yaml=include_yaml)
    if not report.ok and report.duplicate_ids:
        logger.warning(
            "Duplicate benchmark ids present",
            extra={"extra_fields": {"duplicates": report.duplicate_ids[:5]}},
        )

    items = registry.items
    if category_filter:
        items = [i for i in items if i.category == category_filter]
    if limit is not None:
        items = items[:limit]

    active_runner = runner or create_runner(model)
    system_prompt = load_system_prompt()

    item_scores: list[RubricScore] = []
    traces: list[EvaluationTraceItem] = []
    failures = 0

    for item in items:
        try:
            response = active_runner.generate(item.question, system_prompt=system_prompt)
        except RunnerError as exc:
            failures += 1
            logger.error(
                "Generation failed",
                extra={"extra_fields": {"benchmark_id": item.id, "error": str(exc)}},
            )
            response = ""
        score = score_response(item=item, response=response, scoring_mode=scoring_mode)
        item_scores.append(score)
        traces.append(
            EvaluationTraceItem(
                benchmark_id=item.id,
                category=item.category.value,
                question=item.question,
                reference_answer=item.reference_answer,
                model_answer=response,
                accuracy=score.accuracy,
                completeness=score.completeness,
                relevance=score.relevance,
            )
        )

    category_scores_raw: dict[BenchmarkCategory, float] = {}
    for category in BenchmarkCategory:
        cat_scores = [s for s in item_scores if s.category == category]
        if not cat_scores:
            continue
        weights = [
            next(i.weight for i in items if i.id == s.benchmark_id)
            for s in cat_scores
        ]
        category_scores_raw[category] = aggregate_category_score(cat_scores, weights)

    aas_result = compute_aas(category_scores_raw)
    elapsed = round(time.perf_counter() - start, 3)

    result = EvaluationRunResult(
        run_id=new_run_id(),
        timestamp=datetime.now(timezone.utc).isoformat(),
        model=active_runner.model_name,
        provider=active_runner.provider,
        category_scores=aas_result.category_scores,
        aas=aas_result.aas,
        benchmark_count=len(items),
        execution_time=elapsed,
        item_scores=[s.model_dump() for s in item_scores],
        traces=traces,
        metadata={
            "failures": failures,
            "include_yaml": include_yaml,
            "scoring_mode": ScoringMode(scoring_mode).value
            if isinstance(scoring_mode, str)
            else scoring_mode.value,
            "missing_categories": aas_result.missing_categories,
            "weighted_contributions": aas_result.weighted_contributions,
        },
    )
    save_run(result)
    logger.info(
        "Evaluation complete",
        extra={
            "extra_fields": {
                "run_id": result.run_id,
                "aas": result.aas,
                "benchmark_count": result.benchmark_count,
                "execution_time": elapsed,
            }
        },
    )
    return result
