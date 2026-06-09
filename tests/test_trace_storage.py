"""Tests for evaluation trace storage and backward compatibility."""

from evaluation.pipeline import run_evaluation
from evaluation.results.storage import (
    EvaluationRunResult,
    EvaluationTraceItem,
    load_run,
    resolve_traces,
    save_run,
)
from evaluation.runners.mock_runner import MockRunner


def test_pipeline_persists_traces(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr("evaluation.results.storage.RESULTS_DIR", tmp_path)

    result = run_evaluation("mock", runner=MockRunner(), include_yaml=False, limit=3)
    assert len(result.traces) == 3
    assert len(result.item_scores) == 3

    trace = result.traces[0]
    assert trace.benchmark_id
    assert trace.category
    assert trace.question
    assert trace.reference_answer
    assert trace.model_answer
    assert 0.0 <= trace.accuracy <= 5.0

    loaded = load_run(result.run_id, tmp_path)
    assert len(loaded.traces) == 3
    assert loaded.traces[0].question == trace.question


def test_legacy_run_backward_compatibility(tmp_path) -> None:
    legacy = EvaluationRunResult(
        run_id="legacy-run",
        timestamp="2026-01-01T00:00:00+00:00",
        model="qwen3:8b",
        provider="qwen",
        category_scores={"saudi_knowledge": 60.0},
        aas=60.0,
        benchmark_count=1,
        execution_time=1.0,
        item_scores=[
            {
                "benchmark_id": "sk-001",
                "category": "saudi_knowledge",
                "accuracy": 1.0,
                "completeness": 2.0,
                "relevance": 1.5,
            }
        ],
    )
    save_run(legacy, tmp_path)
    loaded = load_run("legacy-run", tmp_path)
    traces = resolve_traces(loaded)
    assert len(traces) == 1
    assert traces[0].benchmark_id == "sk-001"
    assert traces[0].accuracy == 1.0
    assert traces[0].question == ""
    assert not traces[0].has_text_trace


def test_trace_item_average_score() -> None:
    trace = EvaluationTraceItem(
        benchmark_id="x",
        category="programming",
        question="q",
        reference_answer="ref",
        model_answer="ans",
        accuracy=3.0,
        completeness=3.0,
        relevance=3.0,
    )
    assert trace.average_score == 3.0
