"""Tests for AAS calculator."""

import pytest

from evaluation.registry.benchmark_schema import BenchmarkCategory
from evaluation.scorers.aas import AASCalculator, AAS_WEIGHTS, compute_aas, validate_weights


def test_weights_sum_to_one() -> None:
    assert validate_weights(AAS_WEIGHTS)


def test_compute_aas_perfect_scores() -> None:
    scores = {category: 100.0 for category in AAS_WEIGHTS}
    result = compute_aas(scores)
    assert result.aas == 100.0
    assert result.weights_valid


def test_compute_aas_missing_category() -> None:
    scores = {BenchmarkCategory.SAUDI_KNOWLEDGE: 80.0}
    result = compute_aas(scores)
    assert result.aas < 80.0
    assert BenchmarkCategory.PROGRAMMING.value in result.missing_categories


def test_calculator_rejects_bad_weights() -> None:
    bad = {BenchmarkCategory.SAUDI_KNOWLEDGE: 0.5}
    with pytest.raises(ValueError):
        AASCalculator(weights=bad)
