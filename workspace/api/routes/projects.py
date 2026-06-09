"""Workspace project routes."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status

from workspace.api.dependencies import CurrentUserId, DbSession, require_workspace_enabled
from workspace.schemas.project import ProjectCreate, ProjectResponse, ProjectUpdate
from workspace.services.authz import WorkspaceForbiddenError
from workspace.services import project_service

router = APIRouter(
    prefix="/projects",
    tags=["projects"],
    dependencies=[Depends(require_workspace_enabled)],
)


def _forbidden_to_http(exc: WorkspaceForbiddenError) -> HTTPException:
    return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(
    payload: ProjectCreate,
    session: DbSession,
    owner_id: CurrentUserId,
) -> ProjectResponse:
    project = project_service.create_project(session, owner_id, payload)
    return ProjectResponse.model_validate(project)


@router.get("", response_model=list[ProjectResponse])
def list_projects(
    session: DbSession,
    owner_id: CurrentUserId,
    include_archived: bool = Query(default=False),
) -> list[ProjectResponse]:
    projects = project_service.list_projects(
        session,
        owner_id,
        include_archived=include_archived,
    )
    return [ProjectResponse.model_validate(project) for project in projects]


@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(
    project_id: uuid.UUID,
    session: DbSession,
    owner_id: CurrentUserId,
) -> ProjectResponse:
    try:
        project = project_service.get_project(session, owner_id, project_id)
    except WorkspaceForbiddenError as exc:
        raise _forbidden_to_http(exc) from exc
    return ProjectResponse.model_validate(project)


@router.patch("/{project_id}", response_model=ProjectResponse)
def update_project(
    project_id: uuid.UUID,
    payload: ProjectUpdate,
    session: DbSession,
    owner_id: CurrentUserId,
) -> ProjectResponse:
    try:
        project = project_service.update_project(session, owner_id, project_id, payload)
    except WorkspaceForbiddenError as exc:
        raise _forbidden_to_http(exc) from exc
    return ProjectResponse.model_validate(project)


@router.post("/{project_id}/archive", response_model=ProjectResponse)
def archive_project(
    project_id: uuid.UUID,
    session: DbSession,
    owner_id: CurrentUserId,
) -> ProjectResponse:
    try:
        project = project_service.archive_project(session, owner_id, project_id)
    except WorkspaceForbiddenError as exc:
        raise _forbidden_to_http(exc) from exc
    return ProjectResponse.model_validate(project)


@router.delete("/{project_id}", response_model=ProjectResponse)
def delete_project(
    project_id: uuid.UUID,
    session: DbSession,
    owner_id: CurrentUserId,
) -> ProjectResponse:
    try:
        project = project_service.delete_project(session, owner_id, project_id)
    except WorkspaceForbiddenError as exc:
        raise _forbidden_to_http(exc) from exc
    return ProjectResponse.model_validate(project)
