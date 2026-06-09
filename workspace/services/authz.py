"""Ownership and authorization helpers for workspace resources."""

from __future__ import annotations

import uuid

from sqlalchemy.orm import Session

from workspace.db.models import Project, ProjectMemory


class WorkspaceForbiddenError(PermissionError):
    """Raised when a user attempts to access a resource they do not own."""


def assert_project_owner(project: Project, owner_id: uuid.UUID) -> None:
    """Raise if the given user is not the project owner."""
    if project.owner_id != owner_id:
        raise WorkspaceForbiddenError("Project access denied")


def get_project_for_owner(
    session: Session,
    project_id: uuid.UUID,
    owner_id: uuid.UUID,
) -> Project:
    """Load a project only when it belongs to the requesting owner."""
    project = session.get(Project, project_id)
    if project is None or project.owner_id != owner_id:
        raise WorkspaceForbiddenError("Project not found or access denied")
    return project


def ensure_owner_scope(owner_id: uuid.UUID, resource_owner_id: uuid.UUID) -> None:
    """Raise if a resource owner_id does not match the authenticated user."""
    if owner_id != resource_owner_id:
        raise WorkspaceForbiddenError("Resource access denied")


def get_memory_for_owner(
    session: Session,
    memory_id: uuid.UUID,
    owner_id: uuid.UUID,
) -> ProjectMemory:
    """Load a memory row only when it belongs to the requesting owner."""
    memory = session.get(ProjectMemory, memory_id)
    if memory is None or memory.owner_id != owner_id:
        raise WorkspaceForbiddenError("Memory not found or access denied")
    return memory
