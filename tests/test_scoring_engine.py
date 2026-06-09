"""Tests for rubric scoring."""

from evaluation.registry.benchmark_schema import BenchmarkCategory, BenchmarkItem, Difficulty
from evaluation.scorers.rubric import aggregate_category_score, score_response


def _item(**kwargs: object) -> BenchmarkItem:
    data = {
        "id": "t1",
        "category": BenchmarkCategory.SAUDI_KNOWLEDGE,
        "difficulty": Difficulty.EASY,
        "weight": 1.0,
        "question": "ما هي رؤية 2030؟",
        "reference_answer": "خطة استراتيجية لتنويع الاقتصاد السعودي",
    }
    data.update(kwargs)
    return BenchmarkItem(**data)


def test_score_exact_match_high() -> None:
    item = _item()
    score = score_response(item=item, response=item.reference_answer)
    assert score.accuracy >= 4.0
    assert score.normalized_0_100 >= 70.0


def test_score_empty_response_zero() -> None:
    item = _item()
    score = score_response(item=item, response="")
    assert score.accuracy == 0.0
    assert score.completeness == 0.0


def test_aggregate_category_score() -> None:
    item = _item()
    s1 = score_response(item=item, response=item.reference_answer)
    s2 = score_response(item=item, response=" unrelated ")
    avg = aggregate_category_score([s1, s2], [1.0, 1.0])
    assert 0.0 <= avg <= 100.0
