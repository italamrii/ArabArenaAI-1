"""Tests for workspace project API (Phase Next Step 2)."""

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


def test_create_project_via_api(api_client, owner_id) -> None:
    response = api_client.post(
        "/api/v1/workspace/projects",
        headers=_headers(owner_id),
        json={"name": "ArabArena AI", "category": "AI", "tags": ["saas"]},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["name"] == "ArabArena AI"
    assert body["owner_id"] == str(owner_id)
    assert body["status"] == "active"


def test_list_projects_only_owner(api_client, owner_id, other_user_id) -> None:
    api_client.post(
        "/api/v1/workspace/projects",
        headers=_headers(owner_id),
        json={"name": "Owner Project"},
    )
    api_client.post(
        "/api/v1/workspace/projects",
        headers=_headers(other_user_id),
        json={"name": "Other Project"},
    )

    response = api_client.get("/api/v1/workspace/projects", headers=_headers(owner_id))
    assert response.status_code == 200
    names = [item["name"] for item in response.json()]
    assert names == ["Owner Project"]


def test_get_own_project(api_client, owner_id) -> None:
    created = api_client.post(
        "/api/v1/workspace/projects",
        headers=_headers(owner_id),
        json={"name": "Readable"},
    ).json()

    response = api_client.get(
        f"/api/v1/workspace/projects/{created['id']}",
        headers=_headers(owner_id),
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Readable"


def test_reject_other_users_project(api_client, owner_id, other_user_id) -> None:
    created = api_client.post(
        "/api/v1/workspace/projects",
        headers=_headers(owner_id),
        json={"name": "Private"},
    ).json()

    response = api_client.get(
        f"/api/v1/workspace/projects/{created['id']}",
        headers=_headers(other_user_id),
    )
    assert response.status_code == 404


def test_update_own_project(api_client, owner_id) -> None:
    created = api_client.post(
        "/api/v1/workspace/projects",
        headers=_headers(owner_id),
        json={"name": "Before"},
    ).json()

    response = api_client.patch(
        f"/api/v1/workspace/projects/{created['id']}",
        headers=_headers(owner_id),
        json={"name": "After", "description": "Updated"},
    )
    assert response.status_code == 200
    assert response.json()["name"] == "After"
    assert response.json()["description"] == "Updated"


def test_archive_own_project(api_client, owner_id) -> None:
    created = api_client.post(
        "/api/v1/workspace/projects",
        headers=_headers(owner_id),
        json={"name": "To Archive"},
    ).json()

    response = api_client.post(
        f"/api/v1/workspace/projects/{created['id']}/archive",
        headers=_headers(owner_id),
    )
    assert response.status_code == 200
    assert response.json()["status"] == "archived"

    listed = api_client.get("/api/v1/workspace/projects", headers=_headers(owner_id))
    assert listed.json() == []


def test_workspace_disabled_blocks_api(disabled_workspace) -> None:
    engine = _make_test_engine()
    init_db(engine)
    configure_session_factory(get_session_factory(engine))
    client = TestClient(create_app())
    try:
        response = client.get(
            "/api/v1/workspace/projects",
            headers={"X-User-Id": str(uuid.uuid4())},
        )
        assert response.status_code == 404
        assert response.json()["detail"] == "Workspace is disabled"
    finally:
        client.close()
        reset_session_factory()


def test_missing_user_header_rejected(api_client) -> None:
    response = api_client.get("/api/v1/workspace/projects")
    assert response.status_code == 401
    assert "X-User-Id" in response.json()["detail"]
