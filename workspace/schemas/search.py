"""Pydantic schemas for workspace memory search."""

from __future__ import annotations

import uuid

from pydantic import BaseModel, ConfigDict, Field

from workspace.schemas.memory import MemoryResponse


class MemorySearchHit(BaseModel):
    """One ranked memory search result."""

    memory: MemoryResponse
    score: float = Field(..., ge=0.0)
    snippet: str | None = None


class MemorySearchResponse(BaseModel):
    """Search response payload."""

    query: str
    items: list[MemorySearchHit]
    total: int


class ContextBuildResult(BaseModel):
    """Output from the project context builder."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    context_text: str
    context_chars: int
    memories_used: list[uuid.UUID]
    context_used: bool = True
