"""Persist RAG evaluation runs separately from standard evaluation runs."""

from __future__ import annotations

import json
from pathlib import Path

from evaluation.config import RESULTS_DIR
from evaluation.results.storage import EvaluationRunResult, list_runs


def rag_result_path(run_id: str, directory: Path | None = None) -> Path:
    out_dir = directory or RESULTS_DIR
    return out_dir / f"rag_{run_id}.json"


def save_rag_run(result: EvaluationRunResult, directory: Path | None = None) -> Path:
    path = rag_result_path(result.run_id, directory)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(result.model_dump_json(indent=2), encoding="utf-8")
    return path


def load_rag_run(run_id: str, directory: Path | None = None) -> EvaluationRunResult:
    path = rag_result_path(run_id, directory)
    if not path.exists():
        raise FileNotFoundError(f"RAG run not found: {run_id}")
    return EvaluationRunResult.model_validate_json(path.read_text(encoding="utf-8"))


def list_rag_runs(directory: Path | None = None) -> list[EvaluationRunResult]:
    out_dir = directory or RESULTS_DIR
    if not out_dir.exists():
        return []
    runs: list[EvaluationRunResult] = []
    for path in sorted(out_dir.glob("rag_*.json"), reverse=True):
        try:
            runs.append(EvaluationRunResult.model_validate_json(path.read_text(encoding="utf-8")))
        except (json.JSONDecodeError, ValueError):
            continue
    return runs
