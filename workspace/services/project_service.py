"""Project CRUD service with owner-scoped access control."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from workspace.db.models import Project, User
from workspace.schemas.project import ProjectCreate, ProjectUpdate
from workspace.services.authz import WorkspaceForbiddenError, get_project_for_owner

PROJECT_STATUS_ACTIVE = "active"
PROJECT_STATUS_ARCHIVED = "archived"
PROJECT_STATUS_DELETED = "deleted"


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _ensure_user(session: Session, owner_id: uuid.UUID) -> User:
    """Ensure a workspace user row exists (dev-friendly bootstrap)."""
    user = session.get(User, owner_id)
    if user is None:
        user = User(id=owner_id)
        session.add(user)
        session.flush()
    return user


def create_project(session: Session, owner_id: uuid.UUID, data: ProjectCreate) -> Project:
    """Create a project owned by the given user."""
    _ensure_user(session, owner_id)
    project = Project(
        owner_id=owner_id,
        name=data.name.strip(),
        description=data.description,
        category=data.category,
        tags=list(data.tags),
        status=PROJECT_STATUS_ACTIVE,
    )
    session.add(project)
    session.flush()
    return project


def get_project(session: Session, owner_id: uuid.UUID, project_id: uuid.UUID) -> Project:
    """Return a project when it belongs to the owner."""
    return get_project_for_owner(session, project_id, owner_id)


def list_projects(
    session: Session,
    owner_id: uuid.UUID,
    *,
    include_archived: bool = False,
    include_deleted: bool = False,
) -> list[Project]:
    """List projects for the owner, excluding archived/deleted by default."""
    stmt = select(Project).where(Project.owner_id == owner_id)
    if not include_archived:
        stmt = stmt.where(Project.status != PROJECT_STATUS_ARCHIVED)
    if not include_deleted:
        stmt = stmt.where(Project.status != PROJECT_STATUS_DELETED)
    stmt = stmt.order_by(Project.updated_at.desc())
    return list(session.scalars(stmt).all())


def update_project(
    session: Session,
    owner_id: uuid.UUID,
    project_id: uuid.UUID,
    data: ProjectUpdate,
) -> Project:
    """Update mutable project fields for the owner."""
    project = get_project_for_owner(session, project_id, owner_id)
    if project.status == PROJECT_STATUS_DELETED:
        raise WorkspaceForbiddenError("Project not found or access denied")

    payload = data.model_dump(exclude_unset=True)
    if "name" in payload and payload["name"] is not None:
        project.name = payload["name"].strip()
    if "description" in payload:
        project.description = payload["description"]
    if "category" in payload:
        project.category = payload["category"]
    if "tags" in payload and payload["tags"] is not None:
        project.tags = list(payload["tags"])

    project.updated_at = _utcnow()
    session.flush()
    return project


def archive_project(session: Session, owner_id: uuid.UUID, project_id: uuid.UUID) -> Project:
    """Soft-archive a project (status=archived)."""
    project = get_project_for_owner(session, project_id, owner_id)
    if project.status == PROJECT_STATUS_DELETED:
        raise WorkspaceForbiddenError("Project not found or access denied")

    project.status = PROJECT_STATUS_ARCHIVED
    project.updated_at = _utcnow()
    session.flush()
    return project


def delete_project(session: Session, owner_id: uuid.UUID, project_id: uuid.UUID) -> Project:
    """Soft-delete a project (status=deleted)."""
    project = get_project_for_owner(session, project_id, owner_id)
    project.status = PROJECT_STATUS_DELETED
    project.updated_at = _utcnow()
    session.flush()
    return project
