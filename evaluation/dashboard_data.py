"""Data loading helpers for the evaluation dashboard (Streamlit-free for testing)."""

from __future__ import annotations

import json
from pathlib import Path

from evaluation.config import REPORTS_DIR, RESULTS_DIR
from evaluation.reports.leaderboard import Leaderboard
from evaluation.results.storage import EvaluationRunResult, EvaluationTraceItem, list_runs, resolve_traces


def load_leaderboard(reports_dir: Path | None = None) -> Leaderboard | None:
    """Load leaderboard.json if present."""
    path = (reports_dir or REPORTS_DIR) / "leaderboard.json"
    if not path.exists():
        return None
    return Leaderboard.model_validate_json(path.read_text(encoding="utf-8"))


def load_all_runs(results_dir: Path | None = None) -> list[EvaluationRunResult]:
    """Load all evaluation run JSON files."""
    runs = list_runs(results_dir)
    return sorted(runs, key=lambda r: r.timestamp, reverse=True)


def load_regression_reports(reports_dir: Path | None = None) -> list[dict[str, str | Path]]:
    """Load regression markdown reports (newest first)."""
    directory = reports_dir or REPORTS_DIR
    if not directory.exists():
        return []

    reports: list[dict[str, str | Path]] = []
    for path in sorted(directory.glob("regression_*.md"), reverse=True):
        run_id = path.stem.replace("regression_", "", 1)
        reports.append(
            {
                "run_id": run_id,
                "path": path,
                "content": path.read_text(encoding="utf-8"),
            }
        )
    return reports


def model_filter_options(runs: list[EvaluationRunResult]) -> list[str]:
    """Unique provider:model labels for filter dropdown."""
    labels = sorted({f"{r.provider}:{r.model}" for r in runs})
    return ["All"] + labels


def run_filter_options(runs: list[EvaluationRunResult]) -> list[str]:
    """Run labels for filter dropdown."""
    return ["All"] + [f"{r.timestamp[:19]} — {r.run_id[:8]}" for r in runs]


def category_filter_options(runs: list[EvaluationRunResult]) -> list[str]:
    """Categories present across runs."""
    categories: set[str] = set()
    for run in runs:
        categories.update(run.category_scores.keys())
    return ["All"] + sorted(categories)


def filter_runs(
    runs: list[EvaluationRunResult],
    *,
    model_label: str = "All",
    run_label: str = "All",
) -> list[EvaluationRunResult]:
    """Apply model and run filters."""
    filtered = runs
    if model_label != "All":
        provider, model = model_label.split(":", 1)
        filtered = [r for r in filtered if r.provider == provider and r.model == model]
    if run_label != "All":
        run_id_prefix = run_label.split("—")[-1].strip()
        filtered = [r for r in filtered if r.run_id.startswith(run_id_prefix)]
    return filtered


def run_label(run: EvaluationRunResult) -> str:
    return f"{run.timestamp[:19]} — {run.run_id[:8]}"


def load_run_json(run_id: str, results_dir: Path | None = None) -> dict:
    """Load raw run JSON as dict."""
    directory = results_dir or RESULTS_DIR
    path = directory / f"{run_id}.json"
    if not path.exists():
        raise FileNotFoundError(f"Run not found: {run_id}")
    return json.loads(path.read_text(encoding="utf-8"))


def dashboard_summary(runs: list[EvaluationRunResult], leaderboard: Leaderboard | None) -> dict[str, int | float | None]:
    """Aggregate stats for overview section."""
    if not runs:
        return {
            "total_runs": 0,
            "latest_aas": None,
            "best_aas": None,
            "latest_benchmark_count": None,
            "models_count": 0,
        }
    models = {f"{r.provider}:{r.model}" for r in runs}
    return {
        "total_runs": len(runs),
        "latest_aas": runs[0].aas,
        "best_aas": max(r.aas for r in runs),
        "latest_benchmark_count": runs[0].benchmark_count,
        "models_count": len(models),
        "leaderboard_entries": len(leaderboard.entries) if leaderboard else 0,
    }


def get_run_traces(run: EvaluationRunResult) -> list[EvaluationTraceItem]:
    """Load traces for a run, including legacy score-only runs."""
    return resolve_traces(run)


def run_has_text_traces(run: EvaluationRunResult) -> bool:
    """True when the run stores question/answer text (not legacy score-only)."""
    return bool(run.traces) and any(trace.has_text_trace for trace in run.traces)


def filter_traces_by_category(
    traces: list[EvaluationTraceItem],
    category: str,
) -> list[EvaluationTraceItem]:
    if category == "All":
        return traces
    return [trace for trace in traces if trace.category == category]


def lowest_scoring_traces(
    traces: list[EvaluationTraceItem],
    *,
    limit: int = 10,
    category: str = "All",
) -> list[EvaluationTraceItem]:
    """Return lowest-scoring benchmark traces for failure analysis."""
    filtered = filter_traces_by_category(traces, category)
    return sorted(filtered, key=lambda trace: trace.average_score)[:limit]


def load_failure_audit(run_id: str, reports_dir: Path | None = None):
    """Load failure audit JSON for a run if present."""
    from evaluation.reports.failure_audit import FailureAuditReport

    path = (reports_dir or REPORTS_DIR) / f"failure_audit_{run_id}.json"
    if not path.exists():
        return None
    return FailureAuditReport.model_validate_json(path.read_text(encoding="utf-8"))


def list_failure_audits(reports_dir: Path | None = None) -> list:
    """Load all failure audit reports (newest first)."""
    from evaluation.reports.failure_audit import FailureAuditReport

    directory = reports_dir or REPORTS_DIR
    if not directory.exists():
        return []
    reports: list[FailureAuditReport] = []
    for path in sorted(directory.glob("failure_audit_*.json"), reverse=True):
        try:
            reports.append(FailureAuditReport.model_validate_json(path.read_text(encoding="utf-8")))
        except ValueError:
            continue
    return reports


def latest_failure_audit_for_run(
    run_id: str,
    reports_dir: Path | None = None,
):
    return load_failure_audit(run_id, reports_dir)


def load_scoring_comparison(run_id: str, reports_dir: Path | None = None):
    """Load scoring comparison JSON for a run if present."""
    from evaluation.reports.scoring_comparison import ScoringComparisonReport

    path = (reports_dir or REPORTS_DIR) / f"scoring_comparison_{run_id}.json"
    if not path.exists():
        return None
    return ScoringComparisonReport.model_validate_json(path.read_text(encoding="utf-8"))


def load_rag_runs(results_dir: Path | None = None):
    """Load all RAG evaluation runs (newest first)."""
    from rag.storage import list_rag_runs

    return list_rag_runs(results_dir)


def load_rag_comparison(rag_run_id: str, reports_dir: Path | None = None):
    """Load RAG comparison report JSON."""
    from evaluation.reports.rag_comparison import RAGComparisonReport

    path = (reports_dir or REPORTS_DIR) / f"rag_comparison_{rag_run_id}.json"
    if not path.exists():
        return None
    return RAGComparisonReport.model_validate_json(path.read_text(encoding="utf-8"))
