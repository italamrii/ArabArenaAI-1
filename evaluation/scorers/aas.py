"""ArabArena Score (AAS) calculator."""

from __future__ import annotations

from pydantic import BaseModel, Field, model_validator

from evaluation.registry.benchmark_schema import BenchmarkCategory

# Phase 4 harness weights (per implementation spec).
# Note: docs/EVALUATION_FRAMEWORK.md uses a related but not identical weight table
# for governance reporting; this module is the executable harness source of truth.
AAS_WEIGHTS: dict[BenchmarkCategory, float] = {
    BenchmarkCategory.SAUDI_KNOWLEDGE: 0.30,
    BenchmarkCategory.ARABIC_REASONING: 0.20,
    BenchmarkCategory.BUSINESS: 0.15,
    BenchmarkCategory.GOVERNMENT: 0.15,
    BenchmarkCategory.PROGRAMMING: 0.10,
    BenchmarkCategory.TRANSLATION: 0.05,
    BenchmarkCategory.SUMMARIZATION: 0.05,
}


class AASResult(BaseModel):
    """Structured AAS output."""

    aas: float = Field(ge=0.0, le=100.0)
    weighted_contributions: dict[str, float]
    category_scores: dict[str, float]
    missing_categories: list[str] = Field(default_factory=list)
    weights_valid: bool = True


def validate_weights(weights: dict[BenchmarkCategory, float]) -> bool:
    """Validate category weights sum to ~1.0."""
    total = sum(weights.values())
    return abs(total - 1.0) < 1e-6


def compute_aas(
    category_scores: dict[BenchmarkCategory, float],
    weights: dict[BenchmarkCategory, float] | None = None,
) -> AASResult:
    """
    Compute weighted ArabArena Score from per-category scores (0-100).

    Missing categories contribute 0 to the weighted sum and are listed separately.
    """
    active_weights = weights or AAS_WEIGHTS
    if not validate_weights(active_weights):
        raise ValueError("AAS weights must sum to 1.0")

    contributions: dict[str, float] = {}
    missing: list[str] = []
    total = 0.0

    for category, weight in active_weights.items():
        score = category_scores.get(category, 0.0)
        if category not in category_scores:
            missing.append(category.value)
        contribution = score * weight
        contributions[category.value] = round(contribution, 4)
        total += contribution

    return AASResult(
        aas=round(total, 2),
        weighted_contributions=contributions,
        category_scores={k.value: v for k, v in category_scores.items()},
        missing_categories=missing,
        weights_valid=True,
    )


class AASCalculator(BaseModel):
    """Independent calculator module with validation helpers."""

    weights: dict[BenchmarkCategory, float] = Field(default_factory=lambda: dict(AAS_WEIGHTS))

    @model_validator(mode="after")
    def check_weights(self) -> AASCalculator:
        if not validate_weights(self.weights):
            raise ValueError("Configured AAS weights must sum to 1.0")
        return self

    def calculate(self, category_scores: dict[BenchmarkCategory, float]) -> AASResult:
        return compute_aas(category_scores, self.weights)
