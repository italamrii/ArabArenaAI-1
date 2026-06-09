"""Tests for regression detection."""

from evaluation.reports.regression_detector import detect_regressions, render_regression_markdown
from evaluation.results.storage import EvaluationRunResult


def _run(run_id: str, aas: float, category_scores: dict[str, float]) -> EvaluationRunResult:
    return EvaluationRunResult(
        run_id=run_id,
        timestamp="2026-01-01T00:00:00+00:00",
        model="mock",
        provider="mock",
        category_scores=category_scores,
        aas=aas,
        benchmark_count=10,
        execution_time=1.0,
    )


def test_detect_category_regression() -> None:
    baseline = _run("b1", 80.0, {"saudi_knowledge": 80.0, "programming": 90.0})
    current = _run("c1", 70.0, {"saudi_knowledge": 70.0, "programming": 90.0})
    report = detect_regressions(baseline, current, threshold=5.0)
    assert report.aas_regressed is True
    saudi = next(r for r in report.category_regressions if r.category == "saudi_knowledge")
    assert saudi.regressed is True


def test_render_markdown_contains_header() -> None:
    baseline = _run("b1", 80.0, {"saudi_knowledge": 80.0})
    current = _run("c1", 82.0, {"saudi_knowledge": 82.0})
    report = detect_regressions(baseline, current)
    md = render_regression_markdown(report)
    assert "# Regression Report" in md
