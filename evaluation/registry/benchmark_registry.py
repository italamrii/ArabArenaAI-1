"""Benchmark registry — loads, validates, and indexes benchmark items."""

from __future__ import annotations

from pathlib import Path

from evaluation.config import BENCHMARKS_YAML_DIR, DATASETS_DIR, DEFAULT_JSONL_FILES, DEFAULT_YAML_GLOB
from evaluation.datasets.jsonl_loader import load_benchmarks_from_jsonl
from evaluation.datasets.yaml_loader import load_benchmarks_from_yaml_dir
from evaluation.logging_config import get_logger
from evaluation.registry.benchmark_schema import (
    BenchmarkCategory,
    BenchmarkItem,
    ValidationReport,
)

logger = get_logger("registry")


class BenchmarkRegistry:
    """Central registry for all benchmark items."""

    def __init__(self) -> None:
        self._items: list[BenchmarkItem] = []
        self._by_id: dict[str, BenchmarkItem] = {}
        self._validation: ValidationReport | None = None

    @property
    def items(self) -> list[BenchmarkItem]:
        return list(self._items)

    @property
    def validation(self) -> ValidationReport | None:
        return self._validation

    def load(
        self,
        *,
        jsonl_dir: Path | None = None,
        jsonl_files: tuple[str, ...] | None = None,
        yaml_dir: Path | None = None,
        include_yaml: bool = True,
    ) -> ValidationReport:
        """Load benchmarks from JSONL and optional YAML sources."""
        collected: list[BenchmarkItem] = []
        issues: list = []
        seen_ids: set[str] = set()

        jdir = jsonl_dir or DATASETS_DIR
        jfiles = jsonl_files if jsonl_files is not None else DEFAULT_JSONL_FILES
        for filename in jfiles:
            path = jdir / filename
            if not path.exists():
                logger.warning("JSONL file not found", extra={"extra_fields": {"path": str(path)}})
                continue
            items, report = load_benchmarks_from_jsonl(path)
            for item in items:
                if item.id in seen_ids:
                    continue
                seen_ids.add(item.id)
                collected.append(item)
            issues.extend(report.issues)

        if include_yaml:
            ydir = yaml_dir or BENCHMARKS_YAML_DIR
            yaml_items, yaml_report = load_benchmarks_from_yaml_dir(ydir, glob_pattern=DEFAULT_YAML_GLOB)
            for item in yaml_items:
                if item.id in seen_ids:
                    continue
                seen_ids.add(item.id)
                collected.append(item)
            issues.extend(yaml_report.issues)

        merged_report = self._merge_and_validate(collected, issues)
        self._validation = merged_report
        self._items = collected
        self._by_id = {item.id: item for item in collected}

        logger.info(
            "Registry loaded",
            extra={
                "extra_fields": {
                    "count": len(collected),
                    "valid": merged_report.valid_count,
                    "duplicates": len(merged_report.duplicate_ids),
                }
            },
        )
        return merged_report

    def get(self, benchmark_id: str) -> BenchmarkItem | None:
        return self._by_id.get(benchmark_id)

    def get_by_category(self, category: BenchmarkCategory) -> list[BenchmarkItem]:
        return [item for item in self._items if item.category == category]

    def categories_present(self) -> set[BenchmarkCategory]:
        return {item.category for item in self._items}

    def count(self) -> int:
        return len(self._items)

    def _merge_and_validate(
        self,
        items: list[BenchmarkItem],
        prior_issues: list,
    ) -> ValidationReport:
        from evaluation.registry.benchmark_schema import ValidationIssue

        seen: dict[str, int] = {}
        duplicates: list[str] = []
        for item in items:
            seen[item.id] = seen.get(item.id, 0) + 1
        for bid, count in seen.items():
            if count > 1:
                duplicates.append(bid)

        issues = list(prior_issues)
        for dup in duplicates:
            issues.append(
                ValidationIssue(
                    source="registry",
                    benchmark_id=dup,
                    message=f"Duplicate benchmark id detected ({seen[dup]} occurrences)",
                )
            )

        invalid_count = len([i for i in issues if i.benchmark_id or i.line])
        return ValidationReport(
            valid_count=len(items) - len(duplicates),
            invalid_count=len(issues),
            duplicate_ids=sorted(set(duplicates)),
            issues=issues,
        )
