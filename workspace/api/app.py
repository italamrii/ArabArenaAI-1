"""FastAPI application for the ArabArena AI workspace layer."""

from __future__ import annotations

from fastapi import FastAPI

from workspace.api.routes.conversations import router as conversations_router
from workspace.api.routes.memories import router as memories_router
from workspace.api.routes.projects import router as projects_router


def create_app() -> FastAPI:
    """Create the workspace FastAPI application."""
    app = FastAPI(
        title="ArabArena AI Workspace API",
        version="0.4.0",
        description="Project, memory, search, and chat API for the workspace layer (Phase Next).",
    )
    app.include_router(projects_router, prefix="/api/v1/workspace")
    app.include_router(memories_router, prefix="/api/v1/workspace")
    app.include_router(conversations_router, prefix="/api/v1/workspace")
    return app


app = create_app()
