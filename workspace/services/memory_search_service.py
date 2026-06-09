"""Owner-scoped local memory search with lightweight ranking."""

from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from workspace.db.models import ProjectMemory
from workspace.schemas.search import MemorySearchHit, MemorySearchResponse
from workspace.services.authz import get_project_for_owner
from workspace.services.text_search import extract_highlight_snippet, rank_memory


def search_memories(
    session: Session,
    owner_id: uuid.UUID,
    project_id: uuid.UUID,
    query: str,
    *,
    include_archived: bool = False,
    memory_type: str | None = None,
    memory_scope: str | None = None,
    limit: int = 20,
) -> MemorySearchResponse:
    """Search project memories with local Arabic/English ranking."""
    get_project_for_owner(session, project_id, owner_id)
    cleaned_query = query.strip()
    if not cleaned_query:
        return MemorySearchResponse(query=cleaned_query, items=[], total=0)

    stmt = select(ProjectMemory).where(
        ProjectMemory.project_id == project_id,
        ProjectMemory.owner_id == owner_id,
    )
    if not include_archived:
        stmt = stmt.where(ProjectMemory.is_archived.is_(False))
    if memory_type:
        stmt = stmt.where(ProjectMemory.memory_type == memory_type)
    if memory_scope:
        stmt = stmt.where(ProjectMemory.memory_scope == memory_scope)

    candidates = list(session.scalars(stmt).all())
    ranked: list[tuple[ProjectMemory, float]] = []
    for memory in candidates:
        document = memory.search_text or memory.content
        score = rank_memory(
            cleaned_query,
            title=memory.title,
            search_text=document,
            is_pinned=memory.is_pinned,
            importance_score=memory.importance_score,
            updated_at=memory.updated_at,
        )
        if score > 0:
            ranked.append((memory, score))

    ranked.sort(key=lambda item: (-item[1], -int(item[0].is_pinned), -item[0].importance_score))
    limited = ranked[: max(1, min(limit, 100))]

    from workspace.schemas.memory import MemoryResponse

    hits: list[MemorySearchHit] = []
    for memory, score in limited:
        snippet = extract_highlight_snippet(memory.content, cleaned_query)
        hits.append(
            MemorySearchHit(
                memory=MemoryResponse.model_validate(memory),
                score=score,
                snippet=snippet or None,
            )
        )

    return MemorySearchResponse(query=cleaned_query, items=hits, total=len(hits))
