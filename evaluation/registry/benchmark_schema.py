"""Pydantic models for benchmark registry items."""

from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, field_validator, model_validator


class BenchmarkCategory(str, Enum):
    """Supported benchmark categories (extensible via enum values)."""

    SAUDI_KNOWLEDGE = "saudi_knowledge"
    ARABIC_REASONING = "arabic_reasoning"
    BUSINESS = "business"
    GOVERNMENT = "government"
    PROGRAMMING = "programming"
    TRANSLATION = "translation"
    SUMMARIZATION = "summarization"

    @classmethod
    def from_raw(cls, value: str) -> BenchmarkCategory:
        """Normalize legacy or alias category names."""
        aliases: dict[str, BenchmarkCategory] = {
            "business_knowledge": cls.BUSINESS,
            "gov": cls.GOVERNMENT,
            "government_services": cls.GOVERNMENT,
        }
        normalized = value.strip().lower().replace(" ", "_")
        if normalized in cls._value2member_map_:
            return cls(normalized)
        if normalized in aliases:
            return aliases[normalized]
        raise ValueError(f"Unsupported benchmark category: {value}")


class Difficulty(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class BenchmarkItem(BaseModel):
    """Single benchmark question with scoring metadata."""

    id: str = Field(..., min_length=1, description="Unique benchmark identifier")
    category: BenchmarkCategory
    difficulty: Difficulty = Difficulty.MEDIUM
    weight: float = Field(default=1.0, gt=0.0)
    question: str = Field(..., min_length=1)
    reference_answer: str = Field(..., min_length=1)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("id")
    @classmethod
    def normalize_id(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Benchmark id cannot be empty")
        return cleaned

    @field_validator("question", "reference_answer")
    @classmethod
    def strip_text(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Text fields cannot be empty")
        return cleaned

    @model_validator(mode="after")
    def validate_weight_for_difficulty(self) -> BenchmarkItem:
        return self


class ValidationIssue(BaseModel):
    """Single validation or load issue."""

    source: str
    line: int | None = None
    benchmark_id: str | None = None
    message: str


class ValidationReport(BaseModel):
    """Aggregate validation report for benchmark loading."""

    valid_count: int = 0
    invalid_count: int = 0
    duplicate_ids: list[str] = Field(default_factory=list)
    issues: list[ValidationIssue] = Field(default_factory=list)

    @property
    def ok(self) -> bool:
        return self.invalid_count == 0 and not self.duplicate_ids
