"""Tests for workspace project service (Phase Next Step 2)."""

from __future__ import annotations

import uuid

import pytest

pytest.importorskip("sqlalchemy")

from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool

from workspace.db.models import User
from workspace.db.session import get_session_factory, init_db
from workspace.schemas.project import ProjectCreate, ProjectUpdate
from workspace.services.authz import WorkspaceForbiddenError
from workspace.services import project_service


@pytest.fixture
def session():
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    init_db(engine)
    factory = get_session_factory(engine)
    db = factory()
    try:
        yield db
    finally:
        db.close()


def test_create_project(session) -> None:
    owner_id = uuid.uuid4()
    project = project_service.create_project(
        session,
        owner_id,
        ProjectCreate(name="ArabArena AI", category="AI", tags=["platform"]),
    )
    session.commit()

    assert project.name == "ArabArena AI"
    assert project.owner_id == owner_id
    assert project.status == "active"
    assert session.get(User, owner_id) is not None


def test_list_projects_only_returns_owner_projects(session) -> None:
    owner_a = uuid.uuid4()
    owner_b = uuid.uuid4()
    project_service.create_project(session, owner_a, ProjectCreate(name="A1"))
    project_service.create_project(session, owner_a, ProjectCreate(name="A2"))
    project_service.create_project(session, owner_b, ProjectCreate(name="B1"))
    session.commit()

    listed = project_service.list_projects(session, owner_a)
    assert len(listed) == 2
    assert all(project.owner_id == owner_a for project in listed)


def test_get_own_project(session) -> None:
    owner_id = uuid.uuid4()
    created = project_service.create_project(session, owner_id, ProjectCreate(name="Mine"))
    session.commit()

    loaded = project_service.get_project(session, owner_id, created.id)
    assert loaded.id == created.id


def test_reject_other_users_project(session) -> None:
    owner_id = uuid.uuid4()
    other_id = uuid.uuid4()
    created = project_service.create_project(session, owner_id, ProjectCreate(name="Private"))
    session.commit()

    with pytest.raises(WorkspaceForbiddenError):
        project_service.get_project(session, other_id, created.id)


def test_update_own_project(session) -> None:
    owner_id = uuid.uuid4()
    created = project_service.create_project(
        session,
        owner_id,
        ProjectCreate(name="Old Name", description="Old"),
    )
    session.commit()

    updated = project_service.update_project(
        session,
        owner_id,
        created.id,
        ProjectUpdate(name="New Name", description="Updated"),
    )
    session.commit()

    assert updated.name == "New Name"
    assert updated.description == "Updated"


def test_archive_own_project(session) -> None:
    owner_id = uuid.uuid4()
    created = project_service.create_project(session, owner_id, ProjectCreate(name="Archive Me"))
    session.commit()

    archived = project_service.archive_project(session, owner_id, created.id)
    session.commit()

    assert archived.status == "archived"
    assert project_service.list_projects(session, owner_id) == []


def test_delete_project_soft_deletes(session) -> None:
    owner_id = uuid.uuid4()
    created = project_service.create_project(session, owner_id, ProjectCreate(name="Delete Me"))
    session.commit()

    deleted = project_service.delete_project(session, owner_id, created.id)
    session.commit()

    assert deleted.status == "deleted"
    assert project_service.list_projects(session, owner_id) == []

    with pytest.raises(WorkspaceForbiddenError):
        project_service.update_project(
            session,
            owner_id,
            created.id,
            ProjectUpdate(name="Nope"),
        )
