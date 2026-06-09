"""Integration test for evaluation pipeline."""

from evaluation.config import RESULTS_DIR
from evaluation.pipeline import run_evaluation
from evaluation.registry.benchmark_schema import BenchmarkCategory
from evaluation.runners.mock_runner import MockRunner


def test_pipeline_with_mock_runner(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr("evaluation.results.storage.RESULTS_DIR", tmp_path)

    runner = MockRunner()
    result = run_evaluation(
        "mock",
        runner=runner,
        include_yaml=False,
        limit=5,
    )
    assert result.benchmark_count == 5
    assert result.provider == "mock"
    assert 0.0 <= result.aas <= 100.0
    assert (tmp_path / f"{result.run_id}.json").exists()


def test_pipeline_category_filter(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr("evaluation.results.storage.RESULTS_DIR", tmp_path)
    result = run_evaluation(
        "mock",
        runner=MockRunner(),
        include_yaml=False,
        category_filter=BenchmarkCategory.GOVERNMENT,
    )
    assert result.benchmark_count == 2
    assert "government" in result.category_scores
