#!/usr/bin/env python3
"""Evaluate Qwen (or other runners) with local Saudi Knowledge Pack RAG."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from evaluation.logging_config import configure_logging, get_logger
from evaluation.registry.benchmark_schema import BenchmarkCategory
from evaluation.reports.rag_comparison import compare_rag_run, write_rag_comparison
from evaluation.runners.runner_factory import SUPPORTED_MODELS, create_runner
from evaluation.scorers.rubric import ScoringMode
from rag.index import build_knowledge_index, summarize_index
from rag.pipeline import run_rag_evaluation
from rag.router import route_query
from rag.retriever import retrieve

logger = get_logger("evaluate_rag")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="ArabArenaAI-1 Local RAG Evaluation")
    parser.add_argument("--model", required=True, choices=sorted(SUPPORTED_MODELS.keys()))
    parser.add_argument("--model-name", default=None)
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--category", default=None, choices=[c.value for c in BenchmarkCategory])
    parser.add_argument("--jsonl-only", action="store_true")
    parser.add_argument(
        "--scoring",
        default=ScoringMode.CALIBRATED.value,
        choices=[mode.value for mode in ScoringMode],
    )
    parser.add_argument("--top-k", type=int, default=3)
    parser.add_argument("--preview-retrieval", action="store_true", help="Print sample retrievals and exit")
    parser.add_argument("--verbose", action="store_true")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    configure_logging()
    if args.verbose:
        import logging

        logging.getLogger("arabarena.eval").setLevel(logging.DEBUG)

    index = build_knowledge_index()
    summary = summarize_index(index)
    print(f"chunks_indexed={summary['chunk_count']} domains={len(summary['domains'])}")

    if args.preview_retrieval:
        sample_questions = [
            "ما هي منصة قوى؟",
            "عرّف «معدل الحرق» (Burn rate) للشركات الناشئة.",
            "ما هي وزارة الاستثمار (MISA) وما دورها؟",
        ]
        for question in sample_questions:
            decision = route_query(question, category="government" if "قوى" in question else "business")
            result = retrieve(question, index, route=decision, top_k=args.top_k)
            print(f"question={question}")
            print(f"  route={decision.route.value} domains={decision.target_domains} rag_used={result.rag_used}")
            for hit in result.hits:
                print(
                    f"  score={hit.score} domain={hit.domain} "
                    f"chunk_id={hit.chunk_id} reason={hit.reason}"
                )
        return 0

    include_yaml = not args.jsonl_only
    category_filter = BenchmarkCategory(args.category) if args.category else None
    runner = create_runner(args.model, model_name=args.model_name)

    try:
        result = run_rag_evaluation(
            args.model,
            runner=runner,
            include_yaml=include_yaml,
            limit=args.limit,
            category_filter=category_filter,
            scoring_mode=args.scoring,
            top_k=args.top_k,
        )
    except Exception as exc:
        logger.error("RAG evaluation failed", extra={"extra_fields": {"error": str(exc)}})
        return 1

    comparison = compare_rag_run(result)
    json_path, md_path = write_rag_comparison(comparison)

    print(f"run_id={result.run_id} rag_aas={result.aas:.2f} benchmarks={result.benchmark_count}")
    print(f"baseline_run_id={comparison.baseline_run_id} baseline_aas={comparison.baseline_aas:.2f}")
    print(f"aas_delta={comparison.aas_delta:+.2f}")
    print(f"rag_result=evaluation/results/rag_{result.run_id}.json")
    print(f"rag_comparison_json={json_path}")
    print(f"rag_comparison_md={md_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
