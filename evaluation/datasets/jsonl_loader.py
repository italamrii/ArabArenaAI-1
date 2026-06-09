"""JSONL benchmark loader with schema validation."""

from __future__ import annotations

import json
from pathlib import Path

from pydantic import ValidationError

from evaluation.logging_config import get_logger
from evaluation.registry.benchmark_schema import (
    BenchmarkCategory,
    BenchmarkItem,
    Difficulty,
    ValidationIssue,
    ValidationReport,
)

logger = get_logger("jsonl_loader")


def load_benchmarks(path: Path | str) -> tuple[list[BenchmarkItem], ValidationReport]:
    """Load and validate benchmarks from a JSONL file."""
    return load_benchmarks_from_jsonl(path)


def load_benchmarks_from_jsonl(path: Path | str) -> tuple[list[BenchmarkItem], ValidationReport]:
    """Load benchmarks from JSONL with validation and duplicate detection."""
    file_path = Path(path)
    items: list[BenchmarkItem] = []
    issues: list[ValidationIssue] = []
    seen_ids: set[str] = set()
    duplicates: list[str] = []

    if not file_path.exists():
        report = ValidationReport(
            valid_count=0,
            invalid_count=1,
            issues=[
                ValidationIssue(source=str(file_path), message="File does not exist"),
            ],
        )
        return items, report

    with file_path.open(encoding="utf-8") as handle:
        for line_no, raw_line in enumerate(handle, start=1):
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            try:
                payload = json.loads(line)
            except json.JSONDecodeError as exc:
                issues.append(
                    ValidationIssue(
                        source=str(file_path),
                        line=line_no,
                        message=f"Invalid JSON: {exc.msg}",
                    )
                )
                continue

            try:
                category_raw = payload.get("category", "")
                category = BenchmarkCategory.from_raw(str(category_raw))
                difficulty_raw = str(payload.get("difficulty", "medium")).lower()
                difficulty = Difficulty(difficulty_raw) if difficulty_raw in Difficulty._value2member_map_ else Difficulty.MEDIUM

                item = BenchmarkItem(
                    id=str(payload["id"]),
                    category=category,
                    difficulty=difficulty,
                    weight=float(payload.get("weight", 1.0)),
                    question=str(payload["question"]),
                    reference_answer=str(
                        payload.get("reference_answer") or payload.get("gold_answer", "")
                    ),
                    metadata={
                        k: v
                        for k, v in payload.items()
                        if k
                        not in {
                            "id",
                            "category",
                            "difficulty",
                            "weight",
                            "question",
                            "reference_answer",
                            "gold_answer",
                        }
                    },
                )
            except (KeyError, ValueError, ValidationError) as exc:
                issues.append(
                    ValidationIssue(
                        source=str(file_path),
                        line=line_no,
                        benchmark_id=str(payload.get("id")) if isinstance(payload, dict) else None,
                        message=f"Schema validation failed: {exc}",
                    )
                )
                continue

            if item.id in seen_ids:
                duplicates.append(item.id)
            seen_ids.add(item.id)
            items.append(item)

    report = ValidationReport(
        valid_count=len(items),
        invalid_count=len(issues) + len(set(duplicates)),
        duplicate_ids=sorted(set(duplicates)),
        issues=issues
        + [
            ValidationIssue(
                source=str(file_path),
                benchmark_id=dup,
                message="Duplicate id within file",
            )
            for dup in sorted(set(duplicates))
        ],
    )

    logger.info(
        "JSONL loaded",
        extra={
            "extra_fields": {
                "path": str(file_path),
                "items": len(items),
                "issues": len(issues),
            }
        },
    )
    return items, report
