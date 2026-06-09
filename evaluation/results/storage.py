"""Evaluation run result models and persistence."""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from evaluation.config import RESULTS_DIR


class EvaluationTraceItem(BaseModel):
    """Full per-benchmark evaluation trace for failure analysis."""

    benchmark_id: str
    category: str
    question: str = ""
    reference_answer: str = ""
    model_answer: str = ""
    accuracy: float = Field(ge=0.0, le=5.0)
    completeness: float = Field(ge=0.0, le=5.0)
    relevance: float = Field(ge=0.0, le=5.0)

    @property
    def average_score(self) -> float:
        return round((self.accuracy + self.completeness + self.relevance) / 3.0, 2)

    @property
    def has_text_trace(self) -> bool:
        return bool(self.question.strip() or self.reference_answer.strip() or self.model_answer.strip())


class EvaluationRunResult(BaseModel):
    """Persisted evaluation run."""

    run_id: str
    timestamp: str
    model: str
    provider: str
    category_scores: dict[str, float]
    aas: float
    benchmark_count: int
    execution_time: float
    item_scores: list[dict[str, Any]] = Field(default_factory=list)
    traces: list[EvaluationTraceItem] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


def resolve_traces(result: EvaluationRunResult) -> list[EvaluationTraceItem]:
    """
    Return evaluation traces for a run.

    New runs store full traces. Legacy runs only have item_scores; those are
    mapped to trace items without question/answer text.
    """
    if result.traces:
        return result.traces
    legacy: list[EvaluationTraceItem] = []
    for entry in result.item_scores:
        legacy.append(
            EvaluationTraceItem(
                benchmark_id=str(entry.get("benchmark_id", "")),
                category=str(entry.get("category", "")),
                accuracy=float(entry.get("accuracy", 0.0)),
                completeness=float(entry.get("completeness", 0.0)),
                relevance=float(entry.get("relevance", 0.0)),
            )
        )
    return legacy


def ensure_results_dir(path: Path | None = None) -> Path:
    directory = path or RESULTS_DIR
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def save_run(result: EvaluationRunResult, directory: Path | None = None) -> Path:
    """Save run result as JSON."""
    out_dir = ensure_results_dir(directory)
    file_path = out_dir / f"{result.run_id}.json"
    file_path.write_text(result.model_dump_json(indent=2), encoding="utf-8")
    return file_path


def load_run(run_id: str, directory: Path | None = None) -> EvaluationRunResult:
    directory = directory or RESULTS_DIR
    path = directory / f"{run_id}.json"
    if not path.exists():
        raise FileNotFoundError(f"Run not found: {run_id}")
    return EvaluationRunResult.model_validate_json(path.read_text(encoding="utf-8"))


def list_runs(directory: Path | None = None) -> list[EvaluationRunResult]:
    directory = directory or RESULTS_DIR
    if not directory.exists():
        return []
    runs: list[EvaluationRunResult] = []
    for path in sorted(directory.glob("*.json")):
        try:
            runs.append(EvaluationRunResult.model_validate_json(path.read_text(encoding="utf-8")))
        except (json.JSONDecodeError, ValueError):
            continue
    return runs


def query_runs(
    *,
    model: str | None = None,
    provider: str | None = None,
    directory: Path | None = None,
) -> list[EvaluationRunResult]:
    runs = list_runs(directory)
    if model:
        runs = [r for r in runs if r.model == model or r.provider == model]
    if provider:
        runs = [r for r in runs if r.provider == provider]
    return runs


def new_run_id() -> str:
    return str(uuid.uuid4())
