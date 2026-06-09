"""Workspace conversation service with project-aware AI responses."""

from __future__ import annotations

import os
import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from workspace.context.context_aware_runner import ContextAwareRunner
from workspace.context.context_builder import build_project_context
from workspace.db.models import Conversation, ConversationMessage
from workspace.db.sqlite_utils import run_with_sqlite_retry
from workspace.schemas.conversation import ConversationCreate, SendMessageResponse
from workspace.schemas.conversation import MessageResponse as MessageResponseSchema
from workspace.services.authz import WorkspaceForbiddenError, get_project_for_owner

DEFAULT_PROVIDER = os.getenv("WORKSPACE_DEFAULT_PROVIDER", "qwen").strip().lower() or "qwen"
DEFAULT_SYSTEM_PROMPT = (
    "أنت مساعد ذكي لمشاريع ArabArena. أجب بالعربية ما لم يطلب المستخدم غير ذلك. "
    "استخدم سياق المشروع عند توفره."
)

_GENERIC_CONVERSATION_TITLES = frozenset(
    {"new conversation", "محادثة جديدة", "new chat", "conversation", "محادثة"}
)


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _get_conversation_for_owner(
    session: Session,
    owner_id: uuid.UUID,
    project_id: uuid.UUID,
    conversation_id: uuid.UUID,
) -> Conversation:
    get_project_for_owner(session, project_id, owner_id)
    conversation = session.get(Conversation, conversation_id)
    if (
        conversation is None
        or conversation.owner_id != owner_id
        or conversation.project_id != project_id
    ):
        raise WorkspaceForbiddenError("Conversation not found or access denied")
    return conversation


def create_conversation(
    session: Session,
    owner_id: uuid.UUID,
    project_id: uuid.UUID,
    data: ConversationCreate,
) -> Conversation:
    """Create a conversation under an owned project."""
    get_project_for_owner(session, project_id, owner_id)
    conversation = Conversation(
        project_id=project_id,
        owner_id=owner_id,
        title=data.title,
    )
    session.add(conversation)
    session.flush()
    return conversation


def list_conversations(
    session: Session,
    owner_id: uuid.UUID,
    project_id: uuid.UUID,
) -> list[Conversation]:
    """List conversations for an owned project."""
    get_project_for_owner(session, project_id, owner_id)
    stmt = (
        select(Conversation)
        .where(
            Conversation.project_id == project_id,
            Conversation.owner_id == owner_id,
        )
        .order_by(Conversation.updated_at.desc())
    )
    return list(session.scalars(stmt).all())


def get_conversation(
    session: Session,
    owner_id: uuid.UUID,
    project_id: uuid.UUID,
    conversation_id: uuid.UUID,
) -> Conversation:
    """Return a single owned conversation."""
    return _get_conversation_for_owner(session, owner_id, project_id, conversation_id)


def _resolve_runner(provider: str | None, model_name: str | None):
    from evaluation.runners.base_runner import RunnerError
    from evaluation.runners.runner_factory import create_runner

    chosen = (provider or DEFAULT_PROVIDER).strip().lower()
    try:
        return create_runner(chosen, model_name=model_name)
    except RunnerError:
        if chosen != "mock":
            return create_runner("mock", model_name=model_name or "mock")
        raise


def _maybe_set_conversation_title(conversation: Conversation, content: str) -> None:
    title = (conversation.title or "").strip()
    if title.lower() in _GENERIC_CONVERSATION_TITLES or not title:
        conversation.title = content.strip()[:80] or title or "محادثة"


def _persist_assistant_message(
    session: Session,
    *,
    conversation: Conversation,
    content: str,
    model: str | None,
    provider: str | None,
    metadata: dict,
) -> ConversationMessage:
    def _write() -> ConversationMessage:
        assistant_message = ConversationMessage(
            conversation_id=conversation.id,
            role="assistant",
            content=content,
            model=model,
            provider=provider,
            metadata_json=metadata,
        )
        session.add(assistant_message)
        conversation.updated_at = _utcnow()
        session.flush()
        session.commit()
        return assistant_message

    return run_with_sqlite_retry(_write)


def send_message(
    session: Session,
    owner_id: uuid.UUID,
    project_id: uuid.UUID,
    conversation_id: uuid.UUID,
    content: str,
    *,
    provider: str | None = None,
    model_name: str | None = None,
    system_prompt: str | None = None,
) -> SendMessageResponse:
    """Store user message, generate AI reply with project context, store assistant message."""
    from evaluation.runners.base_runner import RunnerError

    conversation = _get_conversation_for_owner(session, owner_id, project_id, conversation_id)
    trimmed = content.strip()

    user_message = ConversationMessage(
        conversation_id=conversation.id,
        role="user",
        content=trimmed,
    )
    session.add(user_message)
    _maybe_set_conversation_title(conversation, trimmed)
    session.flush()
    session.commit()

    context_result = build_project_context(
        session,
        owner_id,
        project_id,
        query=trimmed,
    )

    metadata = {
        "context_used": context_result.context_used,
        "memories_used": [str(mid) for mid in context_result.memories_used],
        "context_chars": context_result.context_chars,
    }

    try:
        runner = _resolve_runner(provider, model_name)
        context_runner = ContextAwareRunner(runner, context_result.context_text)
        response_text = context_runner.generate(
            trimmed,
            system_prompt=system_prompt or DEFAULT_SYSTEM_PROMPT,
        )
        metadata["model"] = context_runner.model_name
        metadata["provider"] = context_runner.provider

        assistant_message = _persist_assistant_message(
            session,
            conversation=conversation,
            content=response_text,
            model=context_runner.model_name,
            provider=context_runner.provider,
            metadata=metadata,
        )

        return SendMessageResponse(
            user_message=MessageResponseSchema.model_validate(user_message),
            assistant_message=MessageResponseSchema.model_validate(assistant_message),
            context_used=context_result.context_used,
            memories_used=context_result.memories_used,
            context_chars=context_result.context_chars,
        )
    except RunnerError as exc:
        error_text = f"Model generation failed: {exc}"
        metadata["error"] = error_text
        metadata["provider"] = provider or DEFAULT_PROVIDER
        if model_name:
            metadata["model"] = model_name

        assistant_message = _persist_assistant_message(
            session,
            conversation=conversation,
            content=error_text,
            model=model_name,
            provider=provider or DEFAULT_PROVIDER,
            metadata=metadata,
        )

        return SendMessageResponse(
            user_message=MessageResponseSchema.model_validate(user_message),
            assistant_message=MessageResponseSchema.model_validate(assistant_message),
            error=error_text,
            context_used=context_result.context_used,
            memories_used=context_result.memories_used,
            context_chars=context_result.context_chars,
        )
