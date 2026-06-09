"""Tests for semantic and calibrated scoring."""

from evaluation.registry.benchmark_schema import BenchmarkCategory, BenchmarkItem, Difficulty
from evaluation.reports.scoring_comparison import compare_scoring_on_traces
from evaluation.results.storage import EvaluationRunResult, EvaluationTraceItem
from evaluation.scorers.rubric import ScoringMode, score_response
from evaluation.scorers.semantic import analyze_semantic_match

BURN_RATE_ANSWER = (
    "«معدل الحرق» (Burn rate) هو مقياس يُستخدم لتحديد معدل الإنفاق النقدي "
    "الذي تُحدثه شركة ناشئة خلال فترة زمنية محددة (غالبًا شهريًا). "
    "يساعد على فهم مدى قدرة الشركة على تغطية تكاليفها قبل الوصول للربحية."
)


def _biz_burn_item() -> BenchmarkItem:
    return BenchmarkItem(
        id="biz-001",
        category=BenchmarkCategory.BUSINESS,
        difficulty=Difficulty.MEDIUM,
        weight=1.0,
        question="عرّف «معدل الحرق» (Burn rate) للشركات الناشئة.",
        reference_answer="معدل صرف النقد شهرياً قبل الوصول للربحية.",
    )


def test_semantic_detects_burn_rate_concepts() -> None:
    result = analyze_semantic_match(_biz_burn_item().reference_answer, BURN_RATE_ANSWER)
    assert result.concept_recall >= 0.5
    assert result.similarity >= 0.45
    assert result.matched_concepts


def test_calibrated_burn_rate_scores_higher_than_legacy() -> None:
    item = _biz_burn_item()
    legacy = score_response(item=item, response=BURN_RATE_ANSWER, scoring_mode=ScoringMode.LEGACY)
    calibrated = score_response(item=item, response=BURN_RATE_ANSWER, scoring_mode=ScoringMode.CALIBRATED)

    assert calibrated.accuracy > legacy.accuracy
    assert calibrated.average > legacy.average
    assert calibrated.accuracy >= 4.0
    assert calibrated.matched_concepts
    assert calibrated.score_reason


def test_legacy_mode_unchanged_for_exact_match() -> None:
    item = BenchmarkItem(
        id="sk-001",
        category=BenchmarkCategory.SAUDI_KNOWLEDGE,
        difficulty=Difficulty.EASY,
        weight=1.0,
        question="ما هي رؤية 2030؟",
        reference_answer="خطة استراتيجية لتنويع الاقتصاد السعودي",
    )
    legacy = score_response(item=item, response=item.reference_answer, scoring_mode=ScoringMode.LEGACY)
    assert legacy.accuracy >= 4.0
    assert legacy.scoring_mode == "legacy"
    assert legacy.score_reason == ""


def test_scoring_comparison_report() -> None:
    item = _biz_burn_item()
    trace = EvaluationTraceItem(
        benchmark_id=item.id,
        category=item.category.value,
        question=item.question,
        reference_answer=item.reference_answer,
        model_answer=BURN_RATE_ANSWER,
        accuracy=0.71,
        completeness=5.0,
        relevance=1.5,
    )
    run = EvaluationRunResult(
        run_id="compare-run",
        timestamp="2026-01-01T00:00:00+00:00",
        model="qwen3:8b",
        provider="qwen",
        category_scores={"business": 30.0},
        aas=30.0,
        benchmark_count=1,
        execution_time=1.0,
        traces=[trace],
    )
    report = compare_scoring_on_traces(run, [trace])
    assert report.items_compared == 1
    assert report.calibrated_aas > report.old_aas
    assert report.top_positive_deltas[0].benchmark_id == "biz-001"
    assert report.top_positive_deltas[0].delta > 0
