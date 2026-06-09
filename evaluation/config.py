"""Evaluation harness configuration and path constants."""

from __future__ import annotations

from pathlib import Path

EVAL_ROOT: Path = Path(__file__).resolve().parent
BENCHMARKS_YAML_DIR: Path = EVAL_ROOT / "benchmarks"
DATASETS_DIR: Path = EVAL_ROOT / "datasets"
PROMPTS_DIR: Path = EVAL_ROOT / "prompts"
RESULTS_DIR: Path = EVAL_ROOT / "results"
REPORTS_DIR: Path = EVAL_ROOT / "reports"
REGISTRY_DIR: Path = EVAL_ROOT / "registry"

DEFAULT_JSONL_FILES: tuple[str, ...] = ("starter_benchmarks.jsonl",)
DEFAULT_YAML_GLOB: str = "*.yaml"

# Regression thresholds (aligned with docs/METRICS.md alert thresholds)
DEFAULT_REGRESSION_THRESHOLD: float = 5.0
DEFAULT_AAS_REGRESSION_THRESHOLD: float = 5.0
