"""Pydantic schemas for workspace project memories."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

MemoryScope = Literal["short_term", "long_term"]
MemoryType = Literal[
    "goal",
    "decision",
    "milestone",
    "output",
    "file_summary",
    "note",
    "conversation_summary",
    "session_context",
]


class MemoryCreate(BaseModel):
    memory_scope: MemoryScope = "long_term"
    memory_type: MemoryType
    title: str | None = Field(default=None, max_length=500)
    content: str = Field(..., min_length=1)
    importance_score: int = Field(default=50, ge=0, le=100)
    source_type: str | None = Field(default=None, max_length=50)
    source_id: uuid.UUID | None = None

    @field_validator("content")
    @classmethod
    def strip_content(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("content must not be empty")
        return stripped


class MemoryUpdate(BaseModel):
    memory_scope: MemoryScope | None = None
    memory_type: MemoryType | None = None
    title: str | None = Field(default=None, max_length=500)
    content: str | None = Field(default=None, min_length=1)
    importance_score: int | None = Field(default=None, ge=0, le=100)
    source_type: str | None = Field(default=None, max_length=50)
    source_id: uuid.UUID | None = None

    @field_validator("content")
    @classmethod
    def strip_content(cls, value: str | None) -> str | None:
        if value is None:
            return None
        stripped = value.strip()
        if not stripped:
            raise ValueError("content must not be empty")
        return stripped


class ImportanceUpdate(BaseModel):
    importance_score: int = Field(..., ge=0, le=100)


class MemoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    project_id: uuid.UUID
    owner_id: uuid.UUID
    memory_scope: str
    memory_type: str
    title: str | None
    content: str
    importance_score: int
    is_pinned: bool
    is_archived: bool
    source_type: str | None
    source_id: uuid.UUID | None
    created_at: datetime
    updated_at: datetime


class MemoryListResponse(BaseModel):
    items: list[MemoryResponse]
    total: int
