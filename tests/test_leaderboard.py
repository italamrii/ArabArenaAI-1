"""Tests for leaderboard generation."""

from evaluation.reports.leaderboard import build_leaderboard, resolve_ties, write_leaderboard
from evaluation.results.storage import EvaluationRunResult, save_run


def test_leaderboard_best_run_per_model(tmp_path) -> None:
    runs = [
        EvaluationRunResult(
            run_id="r1",
            timestamp="2026-01-01T00:00:00+00:00",
            model="mock-a",
            provider="mock",
            category_scores={"saudi_knowledge": 70.0},
            aas=70.0,
            benchmark_count=5,
            execution_time=1.0,
        ),
        EvaluationRunResult(
            run_id="r2",
            timestamp="2026-01-02T00:00:00+00:00",
            model="mock-a",
            provider="mock",
            category_scores={"saudi_knowledge": 85.0},
            aas=85.0,
            benchmark_count=5,
            execution_time=1.0,
        ),
    ]
    for run in runs:
        save_run(run, tmp_path)

    board = build_leaderboard(tmp_path)
    assert len(board.entries) == 1
    assert board.entries[0].best_aas == 85.0
    assert board.entries[0].best_run_id == "r2"
    assert board.entries[0].run_count == 2


def test_write_leaderboard_file(tmp_path) -> None:
    run = EvaluationRunResult(
        run_id="r1",
        timestamp="2026-01-01T00:00:00+00:00",
        model="mock",
        provider="mock",
        category_scores={"saudi_knowledge": 75.0},
        aas=75.0,
        benchmark_count=3,
        execution_time=0.5,
    )
    save_run(run, tmp_path)
    path = write_leaderboard(build_leaderboard(tmp_path), reports_dir=tmp_path)
    assert path.exists()


def test_resolve_ties() -> None:
    from evaluation.reports.leaderboard import LeaderboardEntry

    e1 = LeaderboardEntry(
        model="a",
        provider="mock",
        best_aas=80.0,
        best_run_id="1",
        best_timestamp="t",
        benchmark_count=1,
    )
    e2 = LeaderboardEntry(
        model="b",
        provider="mock",
        best_aas=80.0,
        best_run_id="2",
        best_timestamp="t",
        benchmark_count=1,
    )
    ordered = resolve_ties([e2, e1])
    assert ordered[0].model == "a"
