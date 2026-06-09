"""YAML benchmark loader for legacy benchmark files."""

from __future__ import annotations

from pathlib import Path

import yaml

from evaluation.logging_config import get_logger
from evaluation.registry.benchmark_schema import (
    BenchmarkCategory,
    BenchmarkItem,
    Difficulty,
    ValidationIssue,
    ValidationReport,
)

logger = get_logger("yaml_loader")

YAML_BENCHMARK_NAME_TO_CATEGORY: dict[str, BenchmarkCategory] = {
    "saudi_knowledge": BenchmarkCategory.SAUDI_KNOWLEDGE,
    "arabic_reasoning": BenchmarkCategory.ARABIC_REASONING,
    "business_knowledge": BenchmarkCategory.BUSINESS,
    "programming": BenchmarkCategory.PROGRAMMING,
    "translation": BenchmarkCategory.TRANSLATION,
    "summarization": BenchmarkCategory.SUMMARIZATION,
}

GOVERNMENT_SUBDOMAINS: frozenset[str] = frozenset(
    {
        "government_services",
        "vision_2030",
        "gov",
        "government",
    }
)


def _resolve_category(benchmark_name: str, sub_domain: str | None) -> BenchmarkCategory:
    if sub_domain and sub_domain.lower() in GOVERNMENT_SUBDOMAINS:
        if sub_domain.lower() == "vision_2030":
            return BenchmarkCategory.SAUDI_KNOWLEDGE
        if sub_domain.lower() == "government_services":
            return BenchmarkCategory.GOVERNMENT
    return YAML_BENCHMARK_NAME_TO_CATEGORY.get(
        benchmark_name.lower(),
        BenchmarkCategory.from_raw(benchmark_name),
    )


def load_benchmarks_from_yaml(path: Path | str) -> tuple[list[BenchmarkItem], ValidationReport]:
    """Load benchmarks from a single YAML benchmark file."""
    file_path = Path(path)
    items: list[BenchmarkItem] = []
    issues: list[ValidationIssue] = []

    if not file_path.exists():
        return items, ValidationReport(
            invalid_count=1,
            issues=[ValidationIssue(source=str(file_path), message="File does not exist")],
        )

    with file_path.open(encoding="utf-8") as handle:
        data = yaml.safe_load(handle)

    if not isinstance(data, dict):
        return items, ValidationReport(
            invalid_count=1,
            issues=[ValidationIssue(source=str(file_path), message="Invalid YAML root")],
        )

    benchmark_name = str(data.get("benchmark_name", file_path.stem))
    questions = data.get("sample_questions") or []

    for index, row in enumerate(questions, start=1):
        if not isinstance(row, dict):
            issues.append(
                ValidationIssue(
                    source=str(file_path),
                    line=index,
                    message="Question entry is not a mapping",
                )
            )
            continue
        try:
            sub_domain = row.get("sub_domain")
            category = _resolve_category(benchmark_name, str(sub_domain) if sub_domain else None)
            difficulty_raw = str(row.get("difficulty", "medium")).lower()
            difficulty = (
                Difficulty(difficulty_raw)
                if difficulty_raw in Difficulty._value2member_map_
                else Difficulty.MEDIUM
            )
            item = BenchmarkItem(
                id=str(row["id"]),
                category=category,
                difficulty=difficulty,
                weight=float(row.get("weight", 1.0)),
                question=str(row["question"]),
                reference_answer=str(row.get("gold_answer") or row.get("reference_answer", "")),
                metadata={
                    "source_file": file_path.name,
                    "sub_domain": sub_domain,
                    "source_ref": row.get("source_ref"),
                    "valid_until": row.get("valid_until"),
                },
            )
            items.append(item)
        except (KeyError, ValueError, TypeError) as exc:
            issues.append(
                ValidationIssue(
                    source=str(file_path),
                    line=index,
                    benchmark_id=str(row.get("id")) if isinstance(row, dict) else None,
                    message=f"Failed to parse YAML item: {exc}",
                )
            )

    report = ValidationReport(valid_count=len(items), invalid_count=len(issues), issues=issues)
    logger.info(
        "YAML loaded",
        extra={"extra_fields": {"path": str(file_path), "items": len(items)}},
    )
    return items, report


def load_benchmarks_from_yaml_dir(
    directory: Path | str,
    glob_pattern: str = "*.yaml",
) -> tuple[list[BenchmarkItem], ValidationReport]:
    """Load all YAML benchmarks from a directory."""
    dir_path = Path(directory)
    all_items: list[BenchmarkItem] = []
    all_issues: list[ValidationIssue] = []

    if not dir_path.exists():
        return all_items, ValidationReport(
            invalid_count=1,
            issues=[ValidationIssue(source=str(dir_path), message="Directory does not exist")],
        )

    for yaml_path in sorted(dir_path.glob(glob_pattern)):
        if yaml_path.name == "README.md":
            continue
        items, report = load_benchmarks_from_yaml(yaml_path)
        all_items.extend(items)
        all_issues.extend(report.issues)

    return all_items, ValidationReport(
        valid_count=len(all_items),
        invalid_count=len(all_issues),
        issues=all_issues,
    )
