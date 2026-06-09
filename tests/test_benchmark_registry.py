"""Tests for benchmark registry."""

from pathlib import Path

from evaluation.datasets.jsonl_loader import load_benchmarks_from_jsonl
from evaluation.registry.benchmark_registry import BenchmarkRegistry
from evaluation.registry.benchmark_schema import BenchmarkCategory


def test_registry_loads_jsonl_and_yaml() -> None:
    registry = BenchmarkRegistry()
    report = registry.load(include_yaml=True)
    assert registry.count() > 10
    assert report.valid_count == registry.count()
    assert BenchmarkCategory.SAUDI_KNOWLEDGE in registry.categories_present()
    assert BenchmarkCategory.GOVERNMENT in registry.categories_present()


def test_registry_jsonl_only() -> None:
    registry = BenchmarkRegistry()
    registry.load(include_yaml=False)
    assert registry.count() == 14


def test_get_by_category() -> None:
    registry = BenchmarkRegistry()
    registry.load(include_yaml=False)
    gov = registry.get_by_category(BenchmarkCategory.GOVERNMENT)
    assert len(gov) >= 2
    assert all(item.category == BenchmarkCategory.GOVERNMENT for item in gov)


def test_duplicate_detection_in_file(tmp_path: Path) -> None:
    jsonl = tmp_path / "dup.jsonl"
    jsonl.write_text(
        '{"id":"x1","category":"business","question":"Q?","reference_answer":"A"}\n'
        '{"id":"x1","category":"business","question":"Q2?","reference_answer":"A2"}\n',
        encoding="utf-8",
    )
    items, report = load_benchmarks_from_jsonl(jsonl)
    assert len(items) == 2
    assert "x1" in report.duplicate_ids
