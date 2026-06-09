"""Project memory CRUD service with owner-scoped access control."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from workspace.db.models import ProjectMemory
from workspace.schemas.memory import MemoryCreate, MemoryUpdate
from workspace.services.authz import WorkspaceForbiddenError, get_project_for_owner


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _build_search_text(title: str | None, content: str) -> str:
    parts = [part.strip() for part in (title, content) if part and part.strip()]
    return "\n".join(parts)


def _get_memory_in_project(
    session: Session,
    owner_id: uuid.UUID,
    project_id: uuid.UUID,
    memory_id: uuid.UUID,
) -> ProjectMemory:
    """Load a memory scoped to an owned project."""
    get_project_for_owner(session, project_id, owner_id)
    memory = session.get(ProjectMemory, memory_id)
    if memory is None or memory.owner_id != owner_id or memory.project_id != project_id:
        raise WorkspaceForbiddenError("Memory not found or access denied")
    return memory


def create_memory(
    session: Session,
    owner_id: uuid.UUID,
    project_id: uuid.UUID,
    data: MemoryCreate,
) -> ProjectMemory:
    """Create a memory under an owned project."""
    get_project_for_owner(session, project_id, owner_id)
    memory = ProjectMemory(
        project_id=project_id,
        owner_id=owner_id,
        memory_scope=data.memory_scope,
        memory_type=data.memory_type,
        title=data.title,
        content=data.content,
        importance_score=data.importance_score,
        source_type=data.source_type,
        source_id=data.source_id,
        search_text=_build_search_text(data.title, data.content),
    )
    session.add(memory)
    session.flush()
    return memory


def get_memory(
    session: Session,
    owner_id: uuid.UUID,
    project_id: uuid.UUID,
    memory_id: uuid.UUID,
) -> ProjectMemory:
    """Return a memory when it belongs to the owner and project."""
    return _get_memory_in_project(session, owner_id, project_id, memory_id)


def list_memories(
    session: Session,
    owner_id: uuid.UUID,
    project_id: uuid.UUID,
    *,
    include_archived: bool = False,
    memory_type: str | None = None,
    memory_scope: str | None = None,
) -> list[ProjectMemory]:
    """List memories for an owned project, excluding archived by default."""
    get_project_for_owner(session, project_id, owner_id)
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
    stmt = stmt.order_by(
        ProjectMemory.is_pinned.desc(),
        ProjectMemory.importance_score.desc(),
        ProjectMemory.updated_at.desc(),
    )
    return list(session.scalars(stmt).all())


def update_memory(
    session: Session,
    owner_id: uuid.UUID,
    project_id: uuid.UUID,
    memory_id: uuid.UUID,
    data: MemoryUpdate,
) -> ProjectMemory:
    """Update mutable memory fields."""
    memory = _get_memory_in_project(session, owner_id, project_id, memory_id)
    if memory.is_archived:
        raise WorkspaceForbiddenError("Memory not found or access denied")

    payload = data.model_dump(exclude_unset=True)
    if "memory_scope" in payload:
        memory.memory_scope = payload["memory_scope"]
    if "memory_type" in payload:
        memory.memory_type = payload["memory_type"]
    if "title" in payload:
        memory.title = payload["title"]
    if "content" in payload and payload["content"] is not None:
        memory.content = payload["content"]
    if "importance_score" in payload and payload["importance_score"] is not None:
        memory.importance_score = payload["importance_score"]
    if "source_type" in payload:
        memory.source_type = payload["source_type"]
    if "source_id" in payload:
        memory.source_id = payload["source_id"]

    memory.search_text = _build_search_text(memory.title, memory.content)
    memory.updated_at = _utcnow()
    session.flush()
    return memory


def archive_memory(
    session: Session,
    owner_id: uuid.UUID,
    project_id: uuid.UUID,
    memory_id: uuid.UUID,
) -> ProjectMemory:
    """Archive a memory (is_archived=true)."""
    memory = _get_memory_in_project(session, owner_id, project_id, memory_id)
    memory.is_archived = True
    memory.is_pinned = False
    memory.updated_at = _utcnow()
    session.flush()
    return memory


def delete_memory(
    session: Session,
    owner_id: uuid.UUID,
    project_id: uuid.UUID,
    memory_id: uuid.UUID,
) -> None:
    """Hard-delete a memory row."""
    memory = _get_memory_in_project(session, owner_id, project_id, memory_id)
    session.delete(memory)
    session.flush()


def pin_memory(
    session: Session,
    owner_id: uuid.UUID,
    project_id: uuid.UUID,
    memory_id: uuid.UUID,
) -> ProjectMemory:
    """Pin a memory for priority context inclusion."""
    memory = _get_memory_in_project(session, owner_id, project_id, memory_id)
    if memory.is_archived:
        raise WorkspaceForbiddenError("Memory not found or access denied")
    memory.is_pinned = True
    memory.updated_at = _utcnow()
    session.flush()
    return memory


def unpin_memory(
    session: Session,
    owner_id: uuid.UUID,
    project_id: uuid.UUID,
    memory_id: uuid.UUID,
) -> ProjectMemory:
    """Remove pin from a memory."""
    memory = _get_memory_in_project(session, owner_id, project_id, memory_id)
    memory.is_pinned = False
    memory.updated_at = _utcnow()
    session.flush()
    return memory


def set_importance(
    session: Session,
    owner_id: uuid.UUID,
    project_id: uuid.UUID,
    memory_id: uuid.UUID,
    importance_score: int,
) -> ProjectMemory:
    """Set memory importance score (0–100)."""
    if importance_score < 0 or importance_score > 100:
        raise ValueError("importance_score must be between 0 and 100")

    memory = _get_memory_in_project(session, owner_id, project_id, memory_id)
    if memory.is_archived:
        raise WorkspaceForbiddenError("Memory not found or access denied")
    memory.importance_score = importance_score
    memory.updated_at = _utcnow()
    session.flush()
    return memory
