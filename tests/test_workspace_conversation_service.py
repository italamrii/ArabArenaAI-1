"""Tests for workspace conversation service (Phase Next Step 6)."""

from __future__ import annotations

import uuid
from unittest.mock import patch

import pytest

pytest.importorskip("sqlalchemy")

from sqlalchemy import create_engine

from evaluation.runners.base_runner import RunnerError
from evaluation.runners.mock_runner import MockRunner
from workspace.db.session import get_session_factory, init_db
from workspace.schemas.conversation import ConversationCreate
from workspace.schemas.memory import MemoryCreate
from workspace.schemas.project import ProjectCreate
from workspace.services.authz import WorkspaceForbiddenError
from workspace.services import conversation_service, memory_service, project_service


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
        ProjectCreate(name="Chat Project", description="Chat desc"),
    )
    session.commit()
    return owner_id, project


def test_create_conversation(session, owner_project) -> None:
    owner_id, project = owner_project
    conversation = conversation_service.create_conversation(
        session,
        owner_id,
        project.id,
        ConversationCreate(title="Test chat"),
    )
    session.commit()
    assert conversation.project_id == project.id
    assert conversation.title == "Test chat"


def test_send_message_stores_messages_and_uses_context(session, owner_project) -> None:
    owner_id, project = owner_project
    memory_service.create_memory(
        session,
        owner_id,
        project.id,
        MemoryCreate(memory_type="goal", title="Goal", content="Build workspace chat"),
    )
    conversation = conversation_service.create_conversation(
        session, owner_id, project.id, ConversationCreate(title="Chat")
    )
    session.commit()

    mock = MockRunner("mock")
    with patch(
        "workspace.services.conversation_service._resolve_runner",
        return_value=mock,
    ):
        result = conversation_service.send_message(
            session,
            owner_id,
            project.id,
            conversation.id,
            "What is our goal?",
            provider="mock",
        )
    session.commit()

    assert result.user_message.content == "What is our goal?"
    assert result.assistant_message is not None
    assert result.context_used is True
    assert result.context_chars > 0
    assert result.assistant_message.metadata_json is not None
    assert result.assistant_message.metadata_json.get("context_used") is True


def test_rejects_cross_user_project(session, owner_project) -> None:
    owner_id, project = owner_project
    other_id = uuid.uuid4()
    conversation = conversation_service.create_conversation(
        session, owner_id, project.id, ConversationCreate(title="Private")
    )
    session.commit()

    with pytest.raises(WorkspaceForbiddenError):
        conversation_service.send_message(
            session,
            other_id,
            project.id,
            conversation.id,
            "Hello",
            provider="mock",
        )


def test_handles_model_failure_cleanly(session, owner_project) -> None:
    owner_id, project = owner_project
    conversation = conversation_service.create_conversation(
        session, owner_id, project.id, ConversationCreate(title="Fail chat")
    )
    session.commit()

    failing = MockRunner("mock")

    def _boom(prompt: str, *, system_prompt: str | None = None) -> str:
        raise RunnerError("Ollama unavailable")

    failing.generate = _boom  # type: ignore[method-assign]

    with patch(
        "workspace.services.conversation_service._resolve_runner",
        return_value=failing,
    ):
        result = conversation_service.send_message(
            session,
            owner_id,
            project.id,
            conversation.id,
            "Hello",
            provider="mock",
        )
    session.commit()

    assert result.error is not None
    assert "Model generation failed" in result.error
    assert result.assistant_message is not None
    assert "Model generation failed" in result.assistant_message.content


def test_send_message_commits_user_message_before_generation(session, owner_project) -> None:
    owner_id, project = owner_project
    conversation = conversation_service.create_conversation(
        session, owner_id, project.id, ConversationCreate(title="Timing chat")
    )
    session.commit()

    commits_before_generate: list[int] = []
    original_commit = session.commit

    def tracked_commit() -> None:
        commits_before_generate.append(len(commits_before_generate) + 1)
        original_commit()

    session.commit = tracked_commit  # type: ignore[method-assign]

    mock = MockRunner("mock")
    original_generate = mock.generate

    def slow_generate(prompt: str, *, system_prompt: str | None = None) -> str:
        assert commits_before_generate, "user message should be committed before model call"
        return original_generate(prompt, system_prompt=system_prompt)

    mock.generate = slow_generate  # type: ignore[method-assign]

    with patch(
        "workspace.services.conversation_service._resolve_runner",
        return_value=mock,
    ):
        result = conversation_service.send_message(
            session,
            owner_id,
            project.id,
            conversation.id,
            "When do we commit?",
            provider="mock",
        )

    assert result.user_message.content == "When do we commit?"
    assert result.assistant_message is not None
