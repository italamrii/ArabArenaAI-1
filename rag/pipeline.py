"""RAG evaluation pipeline."""

from __future__ import annotations

import time
from datetime import datetime, timezone

from evaluation.logging_config import get_logger
from evaluation.pipeline import load_system_prompt
from evaluation.registry.benchmark_registry import BenchmarkRegistry
from evaluation.registry.benchmark_schema import BenchmarkCategory
from evaluation.results.storage import EvaluationRunResult, EvaluationTraceItem, new_run_id
from evaluation.runners.base_runner import RunnerError
from evaluation.runners.runner_factory import create_runner
from evaluation.scorers.aas import compute_aas
from evaluation.scorers.rubric import ScoringMode, aggregate_category_score, score_response
from rag.config import DEFAULT_TOP_K, RAG_MIN_CONFIDENCE
from rag.index import build_knowledge_index, summarize_index
from rag.rag_runner import RAGRunner, create_rag_runner
from rag.storage import save_rag_run

logger = get_logger("rag_pipeline")


def run_rag_evaluation(
    model: str,
    *,
    runner=None,
    include_yaml: bool = True,
    limit: int | None = None,
    category_filter: BenchmarkCategory | None = None,
    scoring_mode: ScoringMode | str = ScoringMode.CALIBRATED,
    top_k: int = DEFAULT_TOP_K,
) -> EvaluationRunResult:
    """Execute evaluation with retrieval-augmented generation."""
    start = time.perf_counter()
    index = build_knowledge_index()
    index_summary = summarize_index(index)

    registry = BenchmarkRegistry()
    registry.load(include_yaml=include_yaml)
    items = registry.items
    if category_filter:
        items = [item for item in items if item.category == category_filter]
    if limit is not None:
        items = items[:limit]

    base_runner = runner or create_runner(model)
    rag_runner = RAGRunner(base_runner, index, top_k=top_k)
    system_prompt = load_system_prompt()

    item_scores = []
    traces = []
    rag_details: list[dict] = []
    failures = 0

    for item in items:
        try:
            generation = rag_runner.generate_with_metadata(
                item.question,
                category=item.category.value,
                system_prompt=system_prompt,
            )
            response = generation.answer
        except RunnerError as exc:
            failures += 1
            logger.error(
                "RAG generation failed",
                extra={"extra_fields": {"benchmark_id": item.id, "error": str(exc)}},
            )
            response = ""
            generation = None

        score = score_response(item=item, response=response, scoring_mode=scoring_mode)
        score_payload = score.model_dump(mode="json")
        routing_payload = {
            "route": generation.route if generation else "rag_blocked",
            "rag_used": generation.rag_used if generation else False,
            "routing_reason": generation.routing_reason if generation else "generation failed",
            "detected_entities": generation.detected_entities if generation else [],
            "target_domains": generation.target_domains if generation else [],
            "retrieval_confidence": generation.retrieval_confidence if generation else 0.0,
            "top_chunk_ids": generation.top_chunk_ids if generation else [],
            "top_chunk_scores": generation.top_chunk_scores if generation else [],
            "blocked_reason": generation.blocked_reason if generation else "generation failed",
        }
        score_payload.update(routing_payload)

        if generation is not None:
            score_payload["citations"] = [c.model_dump() for c in generation.citations]
            score_payload["retrieved_chunks"] = generation.retrieved_chunks
            score_payload["retrieval_hits"] = [hit.model_dump() for hit in generation.retrieval_hits]
            rag_details.append(
                {
                    "benchmark_id": item.id,
                    **routing_payload,
                    "citations": score_payload["citations"],
                    "retrieved_chunks": generation.retrieved_chunks,
                    "answer": generation.answer,
                }
            )

        item_scores.append(score_payload)
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
        cat_scores = [score for score in item_scores if score.get("category") == category.value]
        if not cat_scores:
            continue
        from evaluation.scorers.rubric import RubricScore

        rubric_scores = [RubricScore.model_validate(entry) for entry in cat_scores]
        weights = [next(i.weight for i in items if i.id == s.benchmark_id) for s in rubric_scores]
        category_scores_raw[category] = aggregate_category_score(rubric_scores, weights)

    aas_result = compute_aas(category_scores_raw)
    elapsed = round(time.perf_counter() - start, 3)
    mode_value = ScoringMode(scoring_mode).value if isinstance(scoring_mode, str) else scoring_mode.value

    result = EvaluationRunResult(
        run_id=new_run_id(),
        timestamp=datetime.now(timezone.utc).isoformat(),
        model=rag_runner.model_name,
        provider=rag_runner.provider,
        category_scores=aas_result.category_scores,
        aas=aas_result.aas,
        benchmark_count=len(items),
        execution_time=elapsed,
        item_scores=item_scores,
        traces=traces,
        metadata={
            "rag": True,
            "failures": failures,
            "include_yaml": include_yaml,
            "scoring_mode": mode_value,
            "top_k": top_k,
            "routing_enabled": True,
            "rag_min_confidence": RAG_MIN_CONFIDENCE,
            "chunks_indexed": index_summary["chunk_count"],
            "indexed_domains": index_summary["domains"],
            "pack_id": index_summary["pack_id"],
            "rag_details": rag_details,
            "benchmark_ids": [item.id for item in items],
            "missing_categories": aas_result.missing_categories,
            "weighted_contributions": aas_result.weighted_contributions,
        },
    )
    save_rag_run(result)
    logger.info(
        "RAG evaluation complete",
        extra={
            "extra_fields": {
                "run_id": result.run_id,
                "aas": result.aas,
                "chunks_indexed": index_summary["chunk_count"],
            }
        },
    )
    return result
