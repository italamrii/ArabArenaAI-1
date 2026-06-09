#!/usr/bin/env python3
"""ArabArenaAI-1 evaluation CLI."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Ensure repository root is importable when executed as script
_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from evaluation.logging_config import configure_logging, get_logger
from evaluation.pipeline import run_evaluation
from evaluation.registry.benchmark_schema import BenchmarkCategory
from evaluation.reports.leaderboard import build_leaderboard, write_leaderboard
from evaluation.reports.regression_detector import compare_latest_runs, detect_regressions, write_regression_report
from evaluation.reports.failure_audit import generate_failure_audit_for_run
from evaluation.reports.scoring_comparison import compare_scoring_for_run, write_scoring_comparison
from evaluation.results.storage import list_runs, load_run
from evaluation.runners.runner_factory import SUPPORTED_MODELS, create_runner
from evaluation.scorers.rubric import ScoringMode

logger = get_logger("evaluate")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="ArabArenaAI-1 Evaluation Harness")
    parser.add_argument(
        "--model",
        required=True,
        choices=sorted(SUPPORTED_MODELS.keys()),
        help="Model provider key",
    )
    parser.add_argument(
        "--model-name",
        default=None,
        help="Optional provider-specific model name override",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Limit number of benchmarks executed",
    )
    parser.add_argument(
        "--category",
        default=None,
        choices=[c.value for c in BenchmarkCategory],
        help="Filter by benchmark category",
    )
    parser.add_argument(
        "--yaml",
        action="store_true",
        help="Include legacy YAML benchmarks (default: true unless --jsonl-only)",
    )
    parser.add_argument(
        "--jsonl-only",
        action="store_true",
        help="Load JSONL starter benchmarks only",
    )
    parser.add_argument(
        "--baseline-run",
        default=None,
        help="Baseline run id for regression detection",
    )
    parser.add_argument(
        "--skip-leaderboard",
        action="store_true",
        help="Skip leaderboard update",
    )
    parser.add_argument(
        "--skip-regression",
        action="store_true",
        help="Skip regression detection",
    )
    parser.add_argument(
        "--skip-audit",
        action="store_true",
        help="Skip knowledge gap failure audit report",
    )
    parser.add_argument(
        "--audit-limit",
        type=int,
        default=50,
        help="Number of lowest-scoring traces to analyze in failure audit",
    )
    parser.add_argument(
        "--scoring",
        default=ScoringMode.LEGACY.value,
        choices=[mode.value for mode in ScoringMode],
        help="Scoring mode: legacy (overlap) or calibrated (semantic)",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable debug logging",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    configure_logging()
    if args.verbose:
        import logging

        logging.getLogger("arabarena.eval").setLevel(logging.DEBUG)

    include_yaml = not args.jsonl_only
    if args.yaml:
        include_yaml = True

    category_filter = BenchmarkCategory(args.category) if args.category else None

    try:
        runner = create_runner(args.model, model_name=args.model_name)
        result = run_evaluation(
            args.model,
            runner=runner,
            include_yaml=include_yaml,
            limit=args.limit,
            category_filter=category_filter,
            scoring_mode=args.scoring,
        )
    except Exception as exc:
        logger.error("Evaluation failed", extra={"extra_fields": {"error": str(exc)}})
        return 1

    print(f"run_id={result.run_id} aas={result.aas} benchmarks={result.benchmark_count}")

    if not args.skip_leaderboard:
        leaderboard = build_leaderboard()
        path = write_leaderboard(leaderboard)
        print(f"leaderboard={path}")

    if not args.skip_regression:
        report = None
        if args.baseline_run:
            baseline = load_run(args.baseline_run)
            report = detect_regressions(baseline, result)
        else:
            runs = sorted(list_runs(), key=lambda r: r.timestamp)
            if len(runs) >= 2 and runs[-1].run_id == result.run_id:
                report = detect_regressions(runs[-2], result)
            else:
                report = compare_latest_runs(provider=result.provider)

        if report is not None:
            json_path, md_path = write_regression_report(report)
            print(f"regression_json={json_path}")
            print(f"regression_md={md_path}")
        else:
            print("regression=skipped (insufficient history)")

    if not args.skip_audit:
        try:
            _, audit_json, audit_md = generate_failure_audit_for_run(result, limit=args.audit_limit)
            print(f"failure_audit_json={audit_json}")
            print(f"failure_audit_md={audit_md}")
        except ValueError as exc:
            logger.warning("Failure audit skipped", extra={"extra_fields": {"error": str(exc)}})

    try:
        from evaluation.reports.scoring_comparison import compare_scoring_for_run

        comparison = compare_scoring_for_run(result)
        json_path, md_path = write_scoring_comparison(comparison)
        print(f"scoring_comparison_json={json_path}")
        print(f"scoring_comparison_md={md_path}")
        print(
            f"scoring_comparison_aas={comparison.old_aas:.2f}->{comparison.calibrated_aas:.2f} "
            f"delta={comparison.aas_delta:+.2f}"
        )
    except ValueError as exc:
        logger.warning("Scoring comparison skipped", extra={"extra_fields": {"error": str(exc)}})

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
