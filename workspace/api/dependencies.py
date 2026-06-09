"""FastAPI dependencies for the workspace API."""

from __future__ import annotations

import uuid
from collections.abc import Generator
from typing import Annotated

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.orm import Session, sessionmaker

from workspace.config import is_workspace_enabled
from workspace.db.session import create_engine_from_config, get_session_factory

_session_factory: sessionmaker[Session] | None = None


def configure_session_factory(factory: sessionmaker[Session]) -> None:
    """Override the session factory (used in tests)."""
    global _session_factory
    _session_factory = factory


def reset_session_factory() -> None:
    """Reset to lazy initialization from environment config."""
    global _session_factory
    _session_factory = None


def _get_session_factory() -> sessionmaker[Session]:
    global _session_factory
    if _session_factory is None:
        engine = create_engine_from_config()
        _session_factory = get_session_factory(engine)
    return _session_factory


def get_db() -> Generator[Session, None, None]:
    """Yield a database session per request."""
    factory = _get_session_factory()
    session = factory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def require_workspace_enabled() -> None:
    """Block all workspace routes when the feature flag is off."""
    if not is_workspace_enabled():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace is disabled",
        )


def get_current_user_id(
    x_user_id: Annotated[str | None, Header(alias="X-User-Id")] = None,
) -> uuid.UUID:
    """Dev-only auth: resolve the current user from X-User-Id header."""
    if not x_user_id or not x_user_id.strip():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing X-User-Id header",
        )
    try:
        return uuid.UUID(x_user_id.strip())
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid X-User-Id header",
        ) from exc


DbSession = Annotated[Session, Depends(get_db)]
CurrentUserId = Annotated[uuid.UUID, Depends(get_current_user_id)]
