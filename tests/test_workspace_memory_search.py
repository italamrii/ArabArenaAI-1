"""Tests for workspace memory search (Phase Next Step 4)."""

from __future__ import annotations

import uuid

import pytest

pytest.importorskip("sqlalchemy")

from sqlalchemy import create_engine

from workspace.db.session import get_session_factory, init_db
from workspace.schemas.memory import MemoryCreate
from workspace.schemas.project import ProjectCreate
from workspace.services.authz import WorkspaceForbiddenError
from workspace.services import memory_search_service, memory_service, project_service


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
        ProjectCreate(name="Search Project"),
    )
    session.commit()
    return owner_id, project


def test_finds_relevant_memory(session, owner_project) -> None:
    owner_id, project = owner_project
    memory_service.create_memory(
        session,
        owner_id,
        project.id,
        MemoryCreate(memory_type="note", title="PostgreSQL", content="Use PostgreSQL database"),
    )
    memory_service.create_memory(
        session,
        owner_id,
        project.id,
        MemoryCreate(memory_type="note", content="Unrelated cooking recipe"),
    )
    session.commit()

    result = memory_search_service.search_memories(
        session, owner_id, project.id, "PostgreSQL"
    )
    assert result.total >= 1
    assert result.items[0].memory.title == "PostgreSQL"


def test_respects_owner_project_scope(session, owner_project) -> None:
    owner_id, project = owner_project
    other_id = uuid.uuid4()
    memory_service.create_memory(
        session,
        owner_id,
        project.id,
        MemoryCreate(memory_type="goal", content="Secret goal alpha"),
    )
    session.commit()

    with pytest.raises(WorkspaceForbiddenError):
        memory_search_service.search_memories(session, other_id, project.id, "alpha")


def test_excludes_archived_by_default(session, owner_project) -> None:
    owner_id, project = owner_project
    active = memory_service.create_memory(
        session,
        owner_id,
        project.id,
        MemoryCreate(memory_type="note", content="visible keyword"),
    )
    archived = memory_service.create_memory(
        session,
        owner_id,
        project.id,
        MemoryCreate(memory_type="note", content="archived keyword"),
    )
    memory_service.archive_memory(session, owner_id, project.id, archived.id)
    session.commit()

    result = memory_search_service.search_memories(
        session, owner_id, project.id, "keyword"
    )
    ids = {hit.memory.id for hit in result.items}
    assert active.id in ids
    assert archived.id not in ids


def test_ranking_boosts_title_pinned_importance(session, owner_project) -> None:
    owner_id, project = owner_project
    low = memory_service.create_memory(
        session,
        owner_id,
        project.id,
        MemoryCreate(memory_type="note", content="target term here", importance_score=10),
    )
    pinned = memory_service.create_memory(
        session,
        owner_id,
        project.id,
        MemoryCreate(
            memory_type="note",
            title="target term",
            content="less overlap body",
            importance_score=50,
        ),
    )
    memory_service.pin_memory(session, owner_id, project.id, pinned.id)
    high = memory_service.create_memory(
        session,
        owner_id,
        project.id,
        MemoryCreate(
            memory_type="note",
            title="target term priority",
            content="target term details",
            importance_score=95,
        ),
    )
    session.commit()

    result = memory_search_service.search_memories(
        session, owner_id, project.id, "target term"
    )
    ranked_ids = [hit.memory.id for hit in result.items]
    assert ranked_ids.index(high.id) < ranked_ids.index(low.id)
    assert ranked_ids.index(pinned.id) < ranked_ids.index(low.id)
