"""Tests for workspace memory service (Phase Next Step 3)."""

from __future__ import annotations

import uuid

import pytest
from pydantic import ValidationError

pytest.importorskip("sqlalchemy")

from sqlalchemy import create_engine

from workspace.db.session import get_session_factory, init_db
from workspace.schemas.memory import MemoryCreate, MemoryUpdate
from workspace.schemas.project import ProjectCreate
from workspace.services.authz import WorkspaceForbiddenError
from workspace.services import memory_service, project_service


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


@pytest.fixture
def owner_project(session):
    owner_id = uuid.uuid4()
    project = project_service.create_project(
        session,
        owner_id,
        ProjectCreate(name="Memory Project"),
    )
    session.commit()
    return owner_id, project


def test_create_memory_under_own_project(session, owner_project) -> None:
    owner_id, project = owner_project
    memory = memory_service.create_memory(
        session,
        owner_id,
        project.id,
        MemoryCreate(memory_type="goal", content="Launch MVP", title="Goal"),
    )
    session.commit()

    assert memory.project_id == project.id
    assert memory.owner_id == owner_id
    assert memory.content == "Launch MVP"


def test_list_own_memories(session, owner_project) -> None:
    owner_id, project = owner_project
    memory_service.create_memory(
        session,
        owner_id,
        project.id,
        MemoryCreate(memory_type="goal", content="One"),
    )
    memory_service.create_memory(
        session,
        owner_id,
        project.id,
        MemoryCreate(memory_type="note", content="Two"),
    )
    session.commit()

    items = memory_service.list_memories(session, owner_id, project.id)
    assert len(items) == 2


def test_get_own_memory(session, owner_project) -> None:
    owner_id, project = owner_project
    created = memory_service.create_memory(
        session,
        owner_id,
        project.id,
        MemoryCreate(memory_type="decision", content="Use PostgreSQL"),
    )
    session.commit()

    loaded = memory_service.get_memory(session, owner_id, project.id, created.id)
    assert loaded.id == created.id


def test_reject_memory_from_other_owner(session, owner_project) -> None:
    owner_id, project = owner_project
    other_id = uuid.uuid4()
    created = memory_service.create_memory(
        session,
        owner_id,
        project.id,
        MemoryCreate(memory_type="goal", content="Private"),
    )
    session.commit()

    with pytest.raises(WorkspaceForbiddenError):
        memory_service.get_memory(session, other_id, project.id, created.id)


def test_update_own_memory(session, owner_project) -> None:
    owner_id, project = owner_project
    created = memory_service.create_memory(
        session,
        owner_id,
        project.id,
        MemoryCreate(memory_type="note", content="Before"),
    )
    session.commit()

    updated = memory_service.update_memory(
        session,
        owner_id,
        project.id,
        created.id,
        MemoryUpdate(content="After", importance_score=80),
    )
    session.commit()

    assert updated.content == "After"
    assert updated.importance_score == 80


def test_pin_and_unpin_memory(session, owner_project) -> None:
    owner_id, project = owner_project
    created = memory_service.create_memory(
        session,
        owner_id,
        project.id,
        MemoryCreate(memory_type="goal", content="Pinned goal"),
    )
    session.commit()

    pinned = memory_service.pin_memory(session, owner_id, project.id, created.id)
    session.commit()
    assert pinned.is_pinned is True

    unpinned = memory_service.unpin_memory(session, owner_id, project.id, created.id)
    session.commit()
    assert unpinned.is_pinned is False


def test_archive_memory(session, owner_project) -> None:
    owner_id, project = owner_project
    created = memory_service.create_memory(
        session,
        owner_id,
        project.id,
        MemoryCreate(memory_type="milestone", content="Ship routing"),
    )
    session.commit()

    archived = memory_service.archive_memory(session, owner_id, project.id, created.id)
    session.commit()
    assert archived.is_archived is True
    assert memory_service.list_memories(session, owner_id, project.id) == []


def test_importance_validation_in_schema() -> None:
    with pytest.raises(ValidationError):
        MemoryCreate(memory_type="goal", content="Valid", importance_score=101)

    with pytest.raises(ValidationError):
        MemoryCreate(memory_type="goal", content="Valid", importance_score=-1)


def test_set_importance(session, owner_project) -> None:
    owner_id, project = owner_project
    created = memory_service.create_memory(
        session,
        owner_id,
        project.id,
        MemoryCreate(memory_type="goal", content="Important"),
    )
    session.commit()

    updated = memory_service.set_importance(session, owner_id, project.id, created.id, 95)
    session.commit()
    assert updated.importance_score == 95

    with pytest.raises(ValueError):
        memory_service.set_importance(session, owner_id, project.id, created.id, 150)


def test_archived_excluded_by_default(session, owner_project) -> None:
    owner_id, project = owner_project
    active = memory_service.create_memory(
        session,
        owner_id,
        project.id,
        MemoryCreate(memory_type="note", content="Active"),
    )
    archived = memory_service.create_memory(
        session,
        owner_id,
        project.id,
        MemoryCreate(memory_type="note", content="Archived"),
    )
    session.commit()
    memory_service.archive_memory(session, owner_id, project.id, archived.id)
    session.commit()

    items = memory_service.list_memories(session, owner_id, project.id)
    assert len(items) == 1
    assert items[0].id == active.id


def test_delete_memory_hard_deletes(session, owner_project) -> None:
    owner_id, project = owner_project
    created = memory_service.create_memory(
        session,
        owner_id,
        project.id,
        MemoryCreate(memory_type="note", content="Delete me"),
    )
    session.commit()

    memory_service.delete_memory(session, owner_id, project.id, created.id)
    session.commit()

    with pytest.raises(WorkspaceForbiddenError):
        memory_service.get_memory(session, owner_id, project.id, created.id)
