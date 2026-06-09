"""Rubric-based response scoring."""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field, field_validator

from evaluation.registry.benchmark_schema import BenchmarkCategory, BenchmarkItem
from evaluation.scorers.semantic import analyze_semantic_match, semantic_score_to_rubric
from evaluation.scorers.text_utils import normalize_text, overlap_ratio


class ScoringMode(str, Enum):
    LEGACY = "legacy"
    CALIBRATED = "calibrated"


class RubricScore(BaseModel):
    """Structured rubric score for a single response."""

    accuracy: float = Field(ge=0.0, le=5.0)
    completeness: float = Field(ge=0.0, le=5.0)
    relevance: float = Field(ge=0.0, le=5.0)
    benchmark_id: str
    category: BenchmarkCategory
    score_reason: str = ""
    matched_concepts: list[str] = Field(default_factory=list)
    missing_concepts: list[str] = Field(default_factory=list)
    potential_over_penalty: bool = False
    scoring_mode: str = ScoringMode.LEGACY.value

    @property
    def average(self) -> float:
        return (self.accuracy + self.completeness + self.relevance) / 3.0

    @property
    def normalized_0_100(self) -> float:
        return (self.average / 5.0) * 100.0

    @field_validator("accuracy", "completeness", "relevance")
    @classmethod
    def round_scores(cls, value: float) -> float:
        return round(value, 2)


def _legacy_dimensions(
    *,
    reference: str,
    response: str,
    category: BenchmarkCategory,
) -> tuple[float, float, float]:
    overlap = overlap_ratio(reference, response)
    accuracy = min(5.0, overlap * 5.0)

    ref_len = max(len(normalize_text(reference)), 1)
    resp_len = len(normalize_text(response))
    completeness_ratio = min(resp_len / ref_len, 1.25)
    completeness = min(5.0, completeness_ratio * 4.0 + (0.5 if resp_len > 10 else 0.0))
    relevance = min(5.0, (overlap * 3.5) + (1.0 if resp_len > 5 else 0.0))

    if category == BenchmarkCategory.PROGRAMMING:
        accuracy = _score_programming(reference, response)
        completeness = min(5.0, completeness)
        relevance = min(5.0, accuracy * 0.9 + 0.5)

    return round(accuracy, 2), round(completeness, 2), round(relevance, 2)


def score_response(
    *,
    item: BenchmarkItem,
    response: str,
    scoring_mode: ScoringMode | str = ScoringMode.LEGACY,
) -> RubricScore:
    """
    Score a model response against reference using rubric dimensions.

    Uses deterministic heuristics suitable for baseline automation.
    ``calibrated`` mode applies semantic concept matching to reduce paraphrase penalties.
    """
    mode = ScoringMode(scoring_mode) if isinstance(scoring_mode, str) else scoring_mode
    reference = item.reference_answer

    if not response or not response.strip():
        return RubricScore(
            accuracy=0.0,
            completeness=0.0,
            relevance=0.0,
            benchmark_id=item.id,
            category=item.category,
            score_reason="Empty model response",
            scoring_mode=mode.value,
        )

    legacy_accuracy, legacy_completeness, legacy_relevance = _legacy_dimensions(
        reference=reference,
        response=response,
        category=item.category,
    )

    if mode == ScoringMode.LEGACY:
        return RubricScore(
            accuracy=legacy_accuracy,
            completeness=legacy_completeness,
            relevance=legacy_relevance,
            benchmark_id=item.id,
            category=item.category,
            scoring_mode=mode.value,
        )

    semantic = analyze_semantic_match(reference, response)
    semantic_accuracy = semantic_score_to_rubric(semantic.similarity, semantic.concept_recall)
    accuracy = max(legacy_accuracy, semantic_accuracy)

    completeness = legacy_completeness
    if semantic.concept_recall >= 0.5:
        completeness = max(completeness, min(5.0, 3.0 + semantic.concept_recall * 2.0))
    elif semantic.length_ratio > 1.5 and semantic.concept_recall >= 0.35:
        completeness = max(completeness, min(5.0, 4.0))

    question_overlap = overlap_ratio(item.question, response)
    semantic_relevance = min(5.0, semantic.similarity * 4.0 + question_overlap * 0.8 + 0.4)
    relevance = max(legacy_relevance, semantic_relevance)

    potential_over_penalty = (
        legacy_accuracy < 2.0
        and accuracy - legacy_accuracy >= 1.0
        and semantic.concept_recall >= 0.45
    )

    if potential_over_penalty:
        reason = (
            "Calibrated semantic match raised score; legacy overlap likely over-penalized a valid paraphrase"
        )
    elif semantic.concept_recall >= 0.6:
        reason = "Strong concept recall under calibrated semantic scoring"
    else:
        reason = "Moderate semantic alignment with reference concepts"

    return RubricScore(
        accuracy=round(accuracy, 2),
        completeness=round(completeness, 2),
        relevance=round(relevance, 2),
        benchmark_id=item.id,
        category=item.category,
        score_reason=reason,
        matched_concepts=semantic.matched_concepts,
        missing_concepts=semantic.missing_concepts,
        potential_over_penalty=potential_over_penalty,
        scoring_mode=mode.value,
    )


def _score_programming(reference: str, response: str) -> float:
    ref_norm = normalize_text(reference)
    resp_norm = normalize_text(response)
    if ref_norm in resp_norm:
        return 5.0
    overlap = overlap_ratio(reference, response)
    keywords = ["def ", "class ", "select", "function", "return", "import"]
    keyword_hits = sum(1 for kw in keywords if kw in resp_norm and kw in ref_norm)
    bonus = min(2.0, keyword_hits * 0.5)
    return min(5.0, overlap * 4.0 + bonus)


def aggregate_category_score(scores: list[RubricScore], weights: list[float] | None = None) -> float:
    """Weighted average normalized score for a category."""
    if not scores:
        return 0.0
    if weights is None:
        weights = [1.0] * len(scores)
    total_weight = sum(weights)
    if total_weight <= 0:
        return 0.0
    weighted = sum(s.normalized_0_100 * w for s, w in zip(scores, weights))
    return round(weighted / total_weight, 2)
