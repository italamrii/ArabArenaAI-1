"""Tests for workspace database foundation (Phase Next Step 1)."""

from __future__ import annotations

import uuid

import pytest

pytest.importorskip("sqlalchemy")

from sqlalchemy import create_engine

from workspace.db.models import Base, Project, ProjectMemory, User
from workspace.db.session import get_session_factory, init_db
from workspace.services.authz import (
    WorkspaceForbiddenError,
    assert_project_owner,
    ensure_owner_scope,
    get_memory_for_owner,
    get_project_for_owner,
)


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


def test_workspace_models_import() -> None:
    assert User.__tablename__ == "users"
    assert Project.__tablename__ == "projects"
    assert ProjectMemory.__tablename__ == "project_memories"


def test_feature_flag_default_is_false(monkeypatch) -> None:
    monkeypatch.delenv("WORKSPACE_ENABLED", raising=False)
    import importlib

    import workspace.config as config_module

    importlib.reload(config_module)
    assert config_module.WORKSPACE_ENABLED is False
    assert config_module.is_workspace_enabled() is False


def test_is_workspace_enabled_respects_env(monkeypatch) -> None:
    monkeypatch.setenv("WORKSPACE_ENABLED", "true")
    import importlib

    import workspace.config as config_module

    importlib.reload(config_module)
    assert config_module.is_workspace_enabled() is True


def test_get_project_for_owner_success(session) -> None:
    owner = User(email="owner@example.com")
    session.add(owner)
    session.flush()
    project = Project(owner_id=owner.id, name="ArabArena AI", category="AI")
    session.add(project)
    session.commit()

    loaded = get_project_for_owner(session, project.id, owner.id)
    assert loaded.name == "ArabArena AI"


def test_get_project_for_owner_forbidden_wrong_user(session) -> None:
    owner = User(email="owner@example.com")
    other = User(email="other@example.com")
    session.add_all([owner, other])
    session.flush()
    project = Project(owner_id=owner.id, name="Private Project")
    session.add(project)
    session.commit()

    with pytest.raises(WorkspaceForbiddenError):
        get_project_for_owner(session, project.id, other.id)


def test_get_project_for_owner_missing_project(session) -> None:
    owner = User(email="owner@example.com")
    session.add(owner)
    session.commit()

    with pytest.raises(WorkspaceForbiddenError):
        get_project_for_owner(session, uuid.uuid4(), owner.id)


def test_assert_project_owner(session) -> None:
    owner = User(email="owner@example.com")
    other = User(email="other@example.com")
    session.add_all([owner, other])
    session.flush()
    project = Project(owner_id=owner.id, name="Scoped Project")
    session.add(project)
    session.commit()

    assert_project_owner(project, owner.id)
    with pytest.raises(WorkspaceForbiddenError):
        assert_project_owner(project, other.id)


def test_memory_belongs_to_project_owner(session) -> None:
    owner = User(email="owner@example.com")
    other = User(email="other@example.com")
    session.add_all([owner, other])
    session.flush()
    project = Project(owner_id=owner.id, name="Memory Project")
    session.add(project)
    session.flush()
    memory = ProjectMemory(
        project_id=project.id,
        owner_id=owner.id,
        memory_type="goal",
        content="Ship project memory system",
    )
    session.add(memory)
    session.commit()

    loaded = get_memory_for_owner(session, memory.id, owner.id)
    assert loaded.content.startswith("Ship project")

    ensure_owner_scope(owner.id, loaded.owner_id)
    with pytest.raises(WorkspaceForbiddenError):
        get_memory_for_owner(session, memory.id, other.id)
    with pytest.raises(WorkspaceForbiddenError):
        ensure_owner_scope(other.id, loaded.owner_id)


def test_create_engine_requires_database_url(monkeypatch) -> None:
    monkeypatch.delenv("WORKSPACE_DATABASE_URL", raising=False)
    import importlib

    import workspace.config as config_module
    import workspace.db.session as session_module

    importlib.reload(config_module)
    importlib.reload(session_module)

    with pytest.raises(ValueError, match="WORKSPACE_DATABASE_URL"):
        session_module.create_engine_from_config()


def test_all_workspace_tables_registered() -> None:
    table_names = set(Base.metadata.tables.keys())
    expected = {
        "users",
        "projects",
        "project_memories",
        "project_files",
        "project_milestones",
        "conversations",
        "conversation_messages",
        "project_summaries",
        "activity_log",
    }
    assert expected.issubset(table_names)
