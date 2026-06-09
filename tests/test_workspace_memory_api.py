"""Tests for workspace memory API (Phase Next Step 3)."""

from __future__ import annotations

import importlib
import uuid

import pytest

pytest.importorskip("fastapi")
pytest.importorskip("sqlalchemy")

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool

from workspace.api.app import create_app
from workspace.api.dependencies import configure_session_factory, reset_session_factory
from workspace.db.session import get_session_factory, init_db


def _make_test_engine():
    return create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        future=True,
    )


@pytest.fixture
def owner_id() -> uuid.UUID:
    return uuid.uuid4()


@pytest.fixture
def other_user_id() -> uuid.UUID:
    return uuid.uuid4()


@pytest.fixture
def enabled_workspace(monkeypatch):
    monkeypatch.setenv("WORKSPACE_ENABLED", "true")
    import workspace.config as config_module

    importlib.reload(config_module)
    yield
    monkeypatch.setenv("WORKSPACE_ENABLED", "false")
    importlib.reload(config_module)


@pytest.fixture
def disabled_workspace(monkeypatch):
    monkeypatch.setenv("WORKSPACE_ENABLED", "false")
    import workspace.config as config_module

    importlib.reload(config_module)
    yield


@pytest.fixture
def api_client(enabled_workspace):
    engine = _make_test_engine()
    init_db(engine)
    configure_session_factory(get_session_factory(engine))
    client = TestClient(create_app())
    try:
        yield client
    finally:
        client.close()
        reset_session_factory()


def _headers(user_id: uuid.UUID) -> dict[str, str]:
    return {"X-User-Id": str(user_id)}


def _create_project(client: TestClient, owner_id: uuid.UUID, name: str = "Project") -> dict:
    response = client.post(
        "/api/v1/workspace/projects",
        headers=_headers(owner_id),
        json={"name": name},
    )
    assert response.status_code == 201
    return response.json()


def _create_memory(
    client: TestClient,
    owner_id: uuid.UUID,
    project_id: str,
    *,
    content: str = "Memory content",
    memory_type: str = "goal",
) -> dict:
    response = client.post(
        f"/api/v1/workspace/projects/{project_id}/memories",
        headers=_headers(owner_id),
        json={"memory_type": memory_type, "content": content},
    )
    assert response.status_code == 201
    return response.json()


def test_create_memory(api_client, owner_id) -> None:
    project = _create_project(api_client, owner_id)
    memory = _create_memory(api_client, owner_id, project["id"], content="Ship memory system")

    assert memory["content"] == "Ship memory system"
    assert memory["project_id"] == project["id"]
    assert memory["owner_id"] == str(owner_id)


def test_list_memories(api_client, owner_id) -> None:
    project = _create_project(api_client, owner_id)
    _create_memory(api_client, owner_id, project["id"], content="One")
    _create_memory(api_client, owner_id, project["id"], content="Two", memory_type="note")

    response = api_client.get(
        f"/api/v1/workspace/projects/{project['id']}/memories",
        headers=_headers(owner_id),
    )
    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 2
    assert len(body["items"]) == 2


def test_get_memory(api_client, owner_id) -> None:
    project = _create_project(api_client, owner_id)
    created = _create_memory(api_client, owner_id, project["id"])

    response = api_client.get(
        f"/api/v1/workspace/projects/{project['id']}/memories/{created['id']}",
        headers=_headers(owner_id),
    )
    assert response.status_code == 200
    assert response.json()["id"] == created["id"]


def test_update_memory(api_client, owner_id) -> None:
    project = _create_project(api_client, owner_id)
    created = _create_memory(api_client, owner_id, project["id"])

    response = api_client.patch(
        f"/api/v1/workspace/projects/{project['id']}/memories/{created['id']}",
        headers=_headers(owner_id),
        json={"content": "Updated content", "importance_score": 90},
    )
    assert response.status_code == 200
    assert response.json()["content"] == "Updated content"
    assert response.json()["importance_score"] == 90


def test_pin_and_unpin_memory(api_client, owner_id) -> None:
    project = _create_project(api_client, owner_id)
    created = _create_memory(api_client, owner_id, project["id"])

    pin = api_client.post(
        f"/api/v1/workspace/projects/{project['id']}/memories/{created['id']}/pin",
        headers=_headers(owner_id),
    )
    assert pin.status_code == 200
    assert pin.json()["is_pinned"] is True

    unpin = api_client.post(
        f"/api/v1/workspace/projects/{project['id']}/memories/{created['id']}/unpin",
        headers=_headers(owner_id),
    )
    assert unpin.status_code == 200
    assert unpin.json()["is_pinned"] is False


def test_archive_memory(api_client, owner_id) -> None:
    project = _create_project(api_client, owner_id)
    created = _create_memory(api_client, owner_id, project["id"])

    response = api_client.post(
        f"/api/v1/workspace/projects/{project['id']}/memories/{created['id']}/archive",
        headers=_headers(owner_id),
    )
    assert response.status_code == 200
    assert response.json()["is_archived"] is True

    listed = api_client.get(
        f"/api/v1/workspace/projects/{project['id']}/memories",
        headers=_headers(owner_id),
    )
    assert listed.json()["total"] == 0


def test_set_importance(api_client, owner_id) -> None:
    project = _create_project(api_client, owner_id)
    created = _create_memory(api_client, owner_id, project["id"])

    response = api_client.patch(
        f"/api/v1/workspace/projects/{project['id']}/memories/{created['id']}/importance",
        headers=_headers(owner_id),
        json={"importance_score": 75},
    )
    assert response.status_code == 200
    assert response.json()["importance_score"] == 75


def test_delete_memory(api_client, owner_id) -> None:
    project = _create_project(api_client, owner_id)
    created = _create_memory(api_client, owner_id, project["id"])

    response = api_client.delete(
        f"/api/v1/workspace/projects/{project['id']}/memories/{created['id']}",
        headers=_headers(owner_id),
    )
    assert response.status_code == 204

    get_response = api_client.get(
        f"/api/v1/workspace/projects/{project['id']}/memories/{created['id']}",
        headers=_headers(owner_id),
    )
    assert get_response.status_code == 404


def test_missing_user_header_rejected(api_client, owner_id) -> None:
    project = _create_project(api_client, owner_id)
    response = api_client.get(f"/api/v1/workspace/projects/{project['id']}/memories")
    assert response.status_code == 401


def test_workspace_disabled_blocks_memory_routes(disabled_workspace) -> None:
    engine = _make_test_engine()
    init_db(engine)
    configure_session_factory(get_session_factory(engine))
    client = TestClient(create_app())
    try:
        response = client.get(
            f"/api/v1/workspace/projects/{uuid.uuid4()}/memories",
            headers=_headers(uuid.uuid4()),
        )
        assert response.status_code == 404
        assert response.json()["detail"] == "Workspace is disabled"
    finally:
        client.close()
        reset_session_factory()


def test_cross_user_access_rejected(api_client, owner_id, other_user_id) -> None:
    project = _create_project(api_client, owner_id)
    memory = _create_memory(api_client, owner_id, project["id"])

    response = api_client.get(
        f"/api/v1/workspace/projects/{project['id']}/memories/{memory['id']}",
        headers=_headers(other_user_id),
    )
    assert response.status_code == 404
