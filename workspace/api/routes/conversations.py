"""Workspace conversation routes."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, status

from workspace.api.dependencies import CurrentUserId, DbSession, require_workspace_enabled
from workspace.api.routes.projects import _forbidden_to_http
from workspace.schemas.conversation import (
    ConversationCreate,
    ConversationListResponse,
    ConversationResponse,
    MessageCreate,
    MessageResponse,
    SendMessageResponse,
)
from workspace.services.authz import WorkspaceForbiddenError
from workspace.services import conversation_service

router = APIRouter(
    prefix="/projects/{project_id}/conversations",
    tags=["conversations"],
    dependencies=[Depends(require_workspace_enabled)],
)


@router.post("", response_model=ConversationResponse, status_code=status.HTTP_201_CREATED)
def create_conversation(
    project_id: uuid.UUID,
    payload: ConversationCreate,
    session: DbSession,
    owner_id: CurrentUserId,
) -> ConversationResponse:
    try:
        conversation = conversation_service.create_conversation(
            session, owner_id, project_id, payload
        )
    except WorkspaceForbiddenError as exc:
        raise _forbidden_to_http(exc) from exc
    return ConversationResponse.model_validate(conversation)


@router.get("", response_model=ConversationListResponse)
def list_conversations(
    project_id: uuid.UUID,
    session: DbSession,
    owner_id: CurrentUserId,
) -> ConversationListResponse:
    try:
        items = conversation_service.list_conversations(session, owner_id, project_id)
    except WorkspaceForbiddenError as exc:
        raise _forbidden_to_http(exc) from exc
    responses = [ConversationResponse.model_validate(item) for item in items]
    return ConversationListResponse(items=responses, total=len(responses))


@router.get("/{conversation_id}", response_model=ConversationResponse)
def get_conversation(
    project_id: uuid.UUID,
    conversation_id: uuid.UUID,
    session: DbSession,
    owner_id: CurrentUserId,
) -> ConversationResponse:
    try:
        conversation = conversation_service.get_conversation(
            session, owner_id, project_id, conversation_id
        )
    except WorkspaceForbiddenError as exc:
        raise _forbidden_to_http(exc) from exc
    return ConversationResponse.model_validate(conversation)


@router.post(
    "/{conversation_id}/messages",
    response_model=SendMessageResponse,
    status_code=status.HTTP_201_CREATED,
)
def send_message(
    project_id: uuid.UUID,
    conversation_id: uuid.UUID,
    payload: MessageCreate,
    session: DbSession,
    owner_id: CurrentUserId,
) -> SendMessageResponse:
    try:
        return conversation_service.send_message(
            session,
            owner_id,
            project_id,
            conversation_id,
            payload.content,
            provider=payload.provider,
            model_name=payload.model_name,
        )
    except WorkspaceForbiddenError as exc:
        raise _forbidden_to_http(exc) from exc
