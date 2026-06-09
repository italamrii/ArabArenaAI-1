"""Workspace project memory routes."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status

from workspace.api.dependencies import CurrentUserId, DbSession, require_workspace_enabled
from workspace.api.routes.projects import _forbidden_to_http
from workspace.schemas.memory import (
    ImportanceUpdate,
    MemoryCreate,
    MemoryListResponse,
    MemoryResponse,
    MemoryUpdate,
)
from workspace.schemas.search import MemorySearchResponse
from workspace.services.authz import WorkspaceForbiddenError
from workspace.services import memory_search_service, memory_service

router = APIRouter(
    prefix="/projects/{project_id}/memories",
    tags=["memories"],
    dependencies=[Depends(require_workspace_enabled)],
)


@router.post("", response_model=MemoryResponse, status_code=status.HTTP_201_CREATED)
def create_memory(
    project_id: uuid.UUID,
    payload: MemoryCreate,
    session: DbSession,
    owner_id: CurrentUserId,
) -> MemoryResponse:
    try:
        memory = memory_service.create_memory(session, owner_id, project_id, payload)
    except WorkspaceForbiddenError as exc:
        raise _forbidden_to_http(exc) from exc
    return MemoryResponse.model_validate(memory)


@router.get("", response_model=MemoryListResponse)
def list_memories(
    project_id: uuid.UUID,
    session: DbSession,
    owner_id: CurrentUserId,
    include_archived: bool = Query(default=False),
    memory_type: str | None = Query(default=None),
    memory_scope: str | None = Query(default=None),
) -> MemoryListResponse:
    try:
        items = memory_service.list_memories(
            session,
            owner_id,
            project_id,
            include_archived=include_archived,
            memory_type=memory_type,
            memory_scope=memory_scope,
        )
    except WorkspaceForbiddenError as exc:
        raise _forbidden_to_http(exc) from exc
    responses = [MemoryResponse.model_validate(item) for item in items]
    return MemoryListResponse(items=responses, total=len(responses))


@router.get("/search", response_model=MemorySearchResponse)
def search_memories(
    project_id: uuid.UUID,
    session: DbSession,
    owner_id: CurrentUserId,
    q: str = Query(..., min_length=1),
    include_archived: bool = Query(default=False),
    memory_type: str | None = Query(default=None),
    memory_scope: str | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
) -> MemorySearchResponse:
    try:
        return memory_search_service.search_memories(
            session,
            owner_id,
            project_id,
            q,
            include_archived=include_archived,
            memory_type=memory_type,
            memory_scope=memory_scope,
            limit=limit,
        )
    except WorkspaceForbiddenError as exc:
        raise _forbidden_to_http(exc) from exc


@router.get("/{memory_id}", response_model=MemoryResponse)
def get_memory(
    project_id: uuid.UUID,
    memory_id: uuid.UUID,
    session: DbSession,
    owner_id: CurrentUserId,
) -> MemoryResponse:
    try:
        memory = memory_service.get_memory(session, owner_id, project_id, memory_id)
    except WorkspaceForbiddenError as exc:
        raise _forbidden_to_http(exc) from exc
    return MemoryResponse.model_validate(memory)


@router.patch("/{memory_id}", response_model=MemoryResponse)
def update_memory(
    project_id: uuid.UUID,
    memory_id: uuid.UUID,
    payload: MemoryUpdate,
    session: DbSession,
    owner_id: CurrentUserId,
) -> MemoryResponse:
    try:
        memory = memory_service.update_memory(session, owner_id, project_id, memory_id, payload)
    except WorkspaceForbiddenError as exc:
        raise _forbidden_to_http(exc) from exc
    return MemoryResponse.model_validate(memory)


@router.post("/{memory_id}/pin", response_model=MemoryResponse)
def pin_memory(
    project_id: uuid.UUID,
    memory_id: uuid.UUID,
    session: DbSession,
    owner_id: CurrentUserId,
) -> MemoryResponse:
    try:
        memory = memory_service.pin_memory(session, owner_id, project_id, memory_id)
    except WorkspaceForbiddenError as exc:
        raise _forbidden_to_http(exc) from exc
    return MemoryResponse.model_validate(memory)


@router.post("/{memory_id}/unpin", response_model=MemoryResponse)
def unpin_memory(
    project_id: uuid.UUID,
    memory_id: uuid.UUID,
    session: DbSession,
    owner_id: CurrentUserId,
) -> MemoryResponse:
    try:
        memory = memory_service.unpin_memory(session, owner_id, project_id, memory_id)
    except WorkspaceForbiddenError as exc:
        raise _forbidden_to_http(exc) from exc
    return MemoryResponse.model_validate(memory)


@router.post("/{memory_id}/archive", response_model=MemoryResponse)
def archive_memory(
    project_id: uuid.UUID,
    memory_id: uuid.UUID,
    session: DbSession,
    owner_id: CurrentUserId,
) -> MemoryResponse:
    try:
        memory = memory_service.archive_memory(session, owner_id, project_id, memory_id)
    except WorkspaceForbiddenError as exc:
        raise _forbidden_to_http(exc) from exc
    return MemoryResponse.model_validate(memory)


@router.patch("/{memory_id}/importance", response_model=MemoryResponse)
def set_importance(
    project_id: uuid.UUID,
    memory_id: uuid.UUID,
    payload: ImportanceUpdate,
    session: DbSession,
    owner_id: CurrentUserId,
) -> MemoryResponse:
    try:
        memory = memory_service.set_importance(
            session,
            owner_id,
            project_id,
            memory_id,
            payload.importance_score,
        )
    except WorkspaceForbiddenError as exc:
        raise _forbidden_to_http(exc) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc
    return MemoryResponse.model_validate(memory)


@router.delete("/{memory_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_memory(
    project_id: uuid.UUID,
    memory_id: uuid.UUID,
    session: DbSession,
    owner_id: CurrentUserId,
) -> Response:
    try:
        memory_service.delete_memory(session, owner_id, project_id, memory_id)
    except WorkspaceForbiddenError as exc:
        raise _forbidden_to_http(exc) from exc
    return Response(status_code=status.HTTP_204_NO_CONTENT)
