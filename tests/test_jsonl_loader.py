"""Tests for JSONL loader."""

from pathlib import Path

import pytest

from evaluation.datasets.jsonl_loader import load_benchmarks_from_jsonl
from evaluation.registry.benchmark_schema import BenchmarkCategory


def test_load_valid_jsonl(tmp_path: Path) -> None:
    path = tmp_path / "bench.jsonl"
    path.write_text(
        '{"id":"t1","category":"arabic_reasoning","difficulty":"easy","weight":1.0,'
        '"question":"2+2?","reference_answer":"4"}\n',
        encoding="utf-8",
    )
    items, report = load_benchmarks_from_jsonl(path)
    assert len(items) == 1
    assert items[0].category == BenchmarkCategory.ARABIC_REASONING
    assert report.valid_count == 1


def test_invalid_json_reports_error(tmp_path: Path) -> None:
    path = tmp_path / "bad.jsonl"
    path.write_text("{not json}\n", encoding="utf-8")
    items, report = load_benchmarks_from_jsonl(path)
    assert items == []
    assert report.invalid_count >= 1


def test_missing_required_field(tmp_path: Path) -> None:
    path = tmp_path / "missing.jsonl"
    path.write_text('{"id":"m1","category":"business"}\n', encoding="utf-8")
    items, report = load_benchmarks_from_jsonl(path)
    assert items == []
    assert len(report.issues) == 1


def test_starter_file_exists() -> None:
    from evaluation.config import DATASETS_DIR

    path = DATASETS_DIR / "starter_benchmarks.jsonl"
    items, report = load_benchmarks_from_jsonl(path)
    assert len(items) == 14
    assert report.valid_count == 14
    categories = {item.category for item in items}
    assert BenchmarkCategory.GOVERNMENT in categories
    assert BenchmarkCategory.PROGRAMMING in categories
