"""Tests for dashboard data helpers."""

import json
from pathlib import Path

from evaluation.dashboard_data import (
    dashboard_summary,
    filter_runs,
    get_run_traces,
    load_leaderboard,
    load_regression_reports,
    load_run_json,
    lowest_scoring_traces,
    model_filter_options,
    run_has_text_traces,
)
from evaluation.reports.leaderboard import Leaderboard, LeaderboardEntry, write_leaderboard
from evaluation.results.storage import EvaluationRunResult, EvaluationTraceItem, save_run


def _sample_run(run_id: str, aas: float, ts: str) -> EvaluationRunResult:
    return EvaluationRunResult(
        run_id=run_id,
        timestamp=ts,
        model="mock-a",
        provider="mock",
        category_scores={"saudi_knowledge": aas, "government": aas - 5},
        aas=aas,
        benchmark_count=160,
        execution_time=1.5,
    )


def test_load_leaderboard(tmp_path: Path) -> None:
    board = Leaderboard(
        generated_at="2026-01-01T00:00:00+00:00",
        entries=[
            LeaderboardEntry(
                model="mock-a",
                provider="mock",
                best_aas=80.0,
                best_run_id="abc",
                best_timestamp="2026-01-01",
                benchmark_count=160,
            )
        ],
        total_runs=1,
    )
    write_leaderboard(board, reports_dir=tmp_path)
    loaded = load_leaderboard(tmp_path)
    assert loaded is not None
    assert loaded.entries[0].best_aas == 80.0


def test_filter_runs_by_model(tmp_path: Path) -> None:
    runs = [
        _sample_run("r1", 70.0, "2026-01-01T10:00:00+00:00"),
        EvaluationRunResult(
            run_id="r2",
            timestamp="2026-01-02T10:00:00+00:00",
            model="other",
            provider="openai",
            category_scores={"saudi_knowledge": 90.0},
            aas=90.0,
            benchmark_count=160,
            execution_time=2.0,
        ),
    ]
    filtered = filter_runs(runs, model_label="mock:mock-a")
    assert len(filtered) == 1
    assert filtered[0].run_id == "r1"


def test_dashboard_summary(tmp_path: Path) -> None:
    runs = [_sample_run("r1", 75.0, "2026-01-01T10:00:00+00:00")]
    summary = dashboard_summary(runs, None)
    assert summary["total_runs"] == 1
    assert summary["best_aas"] == 75.0


def test_load_regression_reports(tmp_path: Path) -> None:
    path = tmp_path / "regression_abc123.md"
    path.write_text("# Regression Report\n", encoding="utf-8")
    reports = load_regression_reports(tmp_path)
    assert len(reports) == 1
    assert reports[0]["run_id"] == "abc123"


def test_load_run_json(tmp_path: Path) -> None:
    run = _sample_run("json-run", 80.0, "2026-01-01T10:00:00+00:00")
    save_run(run, tmp_path)
    payload = load_run_json("json-run", tmp_path)
    assert payload["aas"] == 80.0


def test_model_filter_options() -> None:
    runs = [_sample_run("r1", 70.0, "2026-01-01T10:00:00+00:00")]
    options = model_filter_options(runs)
    assert "All" in options
    assert "mock:mock-a" in options


def test_lowest_scoring_traces() -> None:
    traces = [
        EvaluationTraceItem(
            benchmark_id="a",
            category="saudi_knowledge",
            question="q1",
            reference_answer="r1",
            model_answer="m1",
            accuracy=4.0,
            completeness=4.0,
            relevance=4.0,
        ),
        EvaluationTraceItem(
            benchmark_id="b",
            category="programming",
            question="q2",
            reference_answer="r2",
            model_answer="m2",
            accuracy=1.0,
            completeness=1.0,
            relevance=1.0,
        ),
    ]
    worst = lowest_scoring_traces(traces, limit=1)
    assert len(worst) == 1
    assert worst[0].benchmark_id == "b"

    filtered = lowest_scoring_traces(traces, limit=5, category="programming")
    assert len(filtered) == 1
    assert filtered[0].benchmark_id == "b"


def test_run_has_text_traces() -> None:
    with_text = EvaluationRunResult(
        run_id="t1",
        timestamp="2026-01-01T00:00:00+00:00",
        model="mock",
        provider="mock",
        category_scores={},
        aas=0.0,
        benchmark_count=1,
        execution_time=1.0,
        traces=[
            EvaluationTraceItem(
                benchmark_id="x",
                category="government",
                question="question?",
                reference_answer="ref",
                model_answer="ans",
                accuracy=1.0,
                completeness=1.0,
                relevance=1.0,
            )
        ],
    )
    legacy = _sample_run("legacy", 70.0, "2026-01-01T10:00:00+00:00")
    assert run_has_text_traces(with_text)
    assert not run_has_text_traces(legacy)
    assert get_run_traces(legacy) == []
