"""Tests for failure classification and knowledge gap audit."""

from __future__ import annotations

from evaluation.registry.benchmark_registry import BenchmarkRegistry
from evaluation.reports.failure_audit import (
    build_failure_audit,
    enrich_traces,
    find_latest_run,
    render_failure_audit_markdown,
    write_failure_audit,
)
from evaluation.reports.failure_classifier import FailureCategory, classify_failure
from evaluation.results.storage import EvaluationRunResult, EvaluationTraceItem, save_run


def _trace(
    *,
    benchmark_id: str = "sk-gov-002",
    category: str = "saudi_knowledge",
    question: str = "ما هي منصة قوى وما خدماتها الرئيسية لأصحاب العمل؟",
    reference: str = "قوى منصة وزارة الموارد البشرية لإدارة العمل ونطاقات.",
    model: str = "منصة للخدمات المصرفية.",
    accuracy: float = 0.5,
    completeness: float = 5.0,
    relevance: float = 1.0,
) -> EvaluationTraceItem:
    return EvaluationTraceItem(
        benchmark_id=benchmark_id,
        category=category,
        question=question,
        reference_answer=reference,
        model_answer=model,
        accuracy=accuracy,
        completeness=completeness,
        relevance=relevance,
    )


def test_classify_knowledge_gap_missing_entity() -> None:
    category, reasons = classify_failure(_trace())
    assert category == FailureCategory.KNOWLEDGE_GAP
    assert any("Missing domain entities" in reason for reason in reasons)


def test_classify_evaluation_gap_high_overlap() -> None:
    trace = _trace(
        model="قوى منصة وزارة الموارد البشرية لإدارة العمل ونطاقات وتصاريح العمل.",
        accuracy=1.2,
        completeness=5.0,
        relevance=2.0,
    )
    category, _ = classify_failure(trace)
    assert category == FailureCategory.EVALUATION_GAP


def test_classify_benchmark_gap_multiple_acceptable() -> None:
    trace = _trace(
        reference="أمثلة مقبولة: أبشر، ناجز، gov.sa — أي منصة رسمية.",
        model="أبشر",
        accuracy=1.0,
        completeness=3.0,
        relevance=1.5,
    )
    category, _ = classify_failure(trace)
    assert category == FailureCategory.BENCHMARK_GAP


def test_enrich_legacy_traces_from_registry() -> None:
    registry = BenchmarkRegistry()
    registry.load(include_yaml=False)
    run = EvaluationRunResult(
        run_id="legacy",
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
                "completeness": 5.0,
                "relevance": 1.5,
            }
        ],
    )
    enriched = enrich_traces(run, registry)
    assert enriched[0].question
    assert enriched[0].reference_answer


def test_build_failure_audit_counts(tmp_path) -> None:
    registry = BenchmarkRegistry()
    registry.load(include_yaml=False)
    run = EvaluationRunResult(
        run_id="audit-run",
        timestamp="2026-01-01T00:00:00+00:00",
        model="qwen3:8b",
        provider="qwen",
        category_scores={"saudi_knowledge": 50.0, "government": 40.0},
        aas=45.0,
        benchmark_count=3,
        execution_time=1.0,
        traces=[
            _trace(benchmark_id="a", accuracy=0.5),
            _trace(
                benchmark_id="b",
                reference="أمثلة مقبولة: Qiwa أو Etimad",
                model="Qiwa",
                accuracy=1.0,
            ),
            _trace(
                benchmark_id="c",
                model="قوى منصة وزارة الموارد البشرية لإدارة العمل ونطاقات.",
                accuracy=1.0,
                completeness=5.0,
                relevance=2.0,
            ),
        ],
    )
    report = build_failure_audit(run, limit=3, registry=registry)
    assert report.total_failures_analyzed == 3
    assert sum(report.classification_counts.values()) == 3
    assert report.priority_knowledge_sources

    json_path, md_path = write_failure_audit(report, tmp_path)
    assert json_path.exists()
    assert "Knowledge Gap Audit" in md_path.read_text(encoding="utf-8")
    assert "Classification Summary" in render_failure_audit_markdown(report)


def test_find_latest_run(tmp_path) -> None:
    older = EvaluationRunResult(
        run_id="old",
        timestamp="2026-01-01T00:00:00+00:00",
        model="qwen3:8b",
        provider="qwen",
        category_scores={},
        aas=60.0,
        benchmark_count=160,
        execution_time=1.0,
    )
    newer = older.model_copy(update={"run_id": "new", "timestamp": "2026-06-01T00:00:00+00:00", "aas": 63.76})
    save_run(older, tmp_path)
    save_run(newer, tmp_path)
    latest = find_latest_run(provider="qwen", model="qwen3:8b", results_dir=tmp_path)
    assert latest is not None
    assert latest.run_id == "new"
