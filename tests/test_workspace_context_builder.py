"""Tests for workspace context builder (Phase Next Step 5)."""

from __future__ import annotations

import uuid

import pytest

pytest.importorskip("sqlalchemy")

from sqlalchemy import create_engine

from workspace.context.context_builder import build_project_context
from workspace.db.session import get_session_factory, init_db
from workspace.schemas.memory import MemoryCreate
from workspace.schemas.project import ProjectCreate
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
        ProjectCreate(name="Context Project", description="Project description"),
    )
    session.commit()
    return owner_id, project


def test_includes_pinned_memories(session, owner_project) -> None:
    owner_id, project = owner_project
    pinned = memory_service.create_memory(
        session,
        owner_id,
        project.id,
        MemoryCreate(memory_type="goal", title="Pinned Goal", content="Launch soon"),
    )
    memory_service.pin_memory(session, owner_id, project.id, pinned.id)
    session.commit()

    result = build_project_context(session, owner_id, project.id)
    assert "Pinned Goal" in result.context_text
    assert pinned.id in result.memories_used


def test_respects_budget(session, owner_project) -> None:
    owner_id, project = owner_project
    for index in range(20):
        memory_service.create_memory(
            session,
            owner_id,
            project.id,
            MemoryCreate(
                memory_type="note",
                title=f"Note {index}",
                content="x" * 400,
                importance_score=90,
            ),
        )
    session.commit()

    result = build_project_context(
        session, owner_id, project.id, max_chars=600
    )
    assert result.context_chars <= 600


def test_includes_relevant_search_hits(session, owner_project) -> None:
    owner_id, project = owner_project
    memory_service.create_memory(
        session,
        owner_id,
        project.id,
        MemoryCreate(memory_type="decision", content="Choose Redis cache"),
    )
    session.commit()

    result = build_project_context(
        session, owner_id, project.id, query="Redis cache"
    )
    assert "Redis" in result.context_text


def test_excludes_other_user_memories(session, owner_project) -> None:
    owner_id, project = owner_project
    other_id = uuid.uuid4()
    other_project = project_service.create_project(
        session, other_id, ProjectCreate(name="Other")
    )
    own = memory_service.create_memory(
        session,
        owner_id,
        project.id,
        MemoryCreate(memory_type="note", content="owner memory"),
    )
    memory_service.create_memory(
        session,
        other_id,
        other_project.id,
        MemoryCreate(memory_type="note", content="other secret"),
    )
    session.commit()

    result = build_project_context(session, owner_id, project.id, query="secret")
    assert "other secret" not in result.context_text
    assert own.id in result.memories_used or "owner memory" in result.context_text
