"""Structured logging configuration for the evaluation harness."""

from __future__ import annotations

import logging
import sys
from typing import Any


class StructuredFormatter(logging.Formatter):
    """Key=value structured log lines for observability."""

    def format(self, record: logging.LogRecord) -> str:
        base: dict[str, Any] = {
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if hasattr(record, "extra_fields") and isinstance(record.extra_fields, dict):
            base.update(record.extra_fields)
        parts = [f"{key}={value}" for key, value in base.items()]
        if record.exc_info:
            parts.append(f"exception={self.formatException(record.exc_info)}")
        return " ".join(parts)


def configure_logging(level: int = logging.INFO) -> None:
    """Configure root logger with structured formatter."""
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(StructuredFormatter())
    root = logging.getLogger("arabarena.eval")
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(level)
    root.propagate = False


def get_logger(name: str) -> logging.Logger:
    """Return a namespaced evaluation logger."""
    return logging.getLogger(f"arabarena.eval.{name}")
