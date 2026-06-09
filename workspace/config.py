"""Workspace configuration and feature flags."""

from __future__ import annotations

import os

# Feature flag — default off; workspace APIs and services stay inactive until enabled.
WORKSPACE_ENABLED = os.getenv("WORKSPACE_ENABLED", "false").lower() in ("1", "true", "yes")

# PostgreSQL connection string for workspace data (required when workspace is enabled).
# Example (local dev only): postgresql+psycopg://arabarena:arabarena@localhost:5432/arabarena_workspace
WORKSPACE_DATABASE_URL = os.getenv("WORKSPACE_DATABASE_URL", "")


def is_workspace_enabled() -> bool:
    """Return True when the workspace layer is explicitly enabled."""
    return WORKSPACE_ENABLED
