#!/usr/bin/env python3
"""Generate knowledge gap / failure classification audit for an evaluation run."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from evaluation.logging_config import configure_logging, get_logger
from evaluation.reports.failure_audit import (
    DEFAULT_ANALYSIS_LIMIT,
    find_latest_run,
    generate_failure_audit_for_run,
)
from evaluation.results.storage import load_run

logger = get_logger("audit_failure")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="ArabArenaAI-1 Knowledge Gap Audit")
    parser.add_argument("--run-id", default=None, help="Evaluation run UUID")
    parser.add_argument("--provider", default="qwen", help="Provider filter when resolving latest run")
    parser.add_argument("--model", default="qwen3:8b", help="Model filter when resolving latest run")
    parser.add_argument(
        "--limit",
        type=int,
        default=DEFAULT_ANALYSIS_LIMIT,
        help="Number of lowest-scoring traces to analyze",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    configure_logging()
    args = parse_args(argv)

    if args.run_id:
        run = load_run(args.run_id)
    else:
        run = find_latest_run(provider=args.provider, model=args.model)
        if run is None:
            logger.error("No matching evaluation run found")
            return 1

    try:
        report, json_path, md_path = generate_failure_audit_for_run(run, limit=args.limit)
    except ValueError as exc:
        logger.error(str(exc))
        return 1

    print(f"run_id={report.run_id} analyzed={report.total_failures_analyzed}")
    print(f"counts={report.classification_counts}")
    print(f"audit_json={json_path}")
    print(f"audit_md={md_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
