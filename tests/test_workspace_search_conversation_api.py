"""Tests for workspace search and conversation API routes."""

from __future__ import annotations

import importlib
import uuid
from unittest.mock import patch

import pytest

pytest.importorskip("fastapi")
pytest.importorskip("sqlalchemy")

from fastapi.testclient import TestClient
from evaluation.runners.mock_runner import MockRunner
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
def enabled_workspace(monkeypatch):
    monkeypatch.setenv("WORKSPACE_ENABLED", "true")
    import workspace.config as config_module

    importlib.reload(config_module)
    yield
    monkeypatch.setenv("WORKSPACE_ENABLED", "false")
    importlib.reload(config_module)


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


def _create_project(client, user_id: uuid.UUID) -> str:
    response = client.post(
        "/api/v1/workspace/projects",
        json={"name": "API Project"},
        headers=_headers(user_id),
    )
    assert response.status_code == 201
    return response.json()["id"]


def test_search_memories_api(api_client, owner_id) -> None:
    project_id = _create_project(api_client, owner_id)
    client = api_client
    create = client.post(
        f"/api/v1/workspace/projects/{project_id}/memories",
        json={"memory_type": "note", "title": "SearchMe", "content": "alpha beta"},
        headers=_headers(owner_id),
    )
    assert create.status_code == 201

    response = client.get(
        f"/api/v1/workspace/projects/{project_id}/memories/search",
        params={"q": "SearchMe"},
        headers=_headers(owner_id),
    )
    assert response.status_code == 200
    body = response.json()
    assert body["total"] >= 1
    assert body["items"][0]["memory"]["title"] == "SearchMe"


def test_conversation_message_api(api_client, owner_id) -> None:
    project_id = _create_project(api_client, owner_id)
    client = api_client
    conv = client.post(
        f"/api/v1/workspace/projects/{project_id}/conversations",
        json={"title": "API Chat"},
        headers=_headers(owner_id),
    )
    assert conv.status_code == 201
    conversation_id = conv.json()["id"]

    with patch(
        "workspace.services.conversation_service._resolve_runner",
        return_value=MockRunner("mock"),
    ):
        msg = client.post(
            f"/api/v1/workspace/projects/{project_id}/conversations/{conversation_id}/messages",
            json={"content": "مرحبا", "provider": "mock"},
            headers=_headers(owner_id),
        )
    assert msg.status_code == 201
    body = msg.json()
    assert body["user_message"]["content"] == "مرحبا"
    assert body["assistant_message"] is not None
    assert body["context_used"] is True
