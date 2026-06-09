"""Tests for SQLite session configuration and retry helpers."""

from __future__ import annotations

import pytest

pytest.importorskip("sqlalchemy")

from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.pool import NullPool, StaticPool

from workspace.db.session import create_engine_from_config
from workspace.db.sqlite_utils import (
    DEFAULT_SQLITE_CONNECT_ARGS,
    is_database_locked_error,
    run_with_sqlite_retry,
)


def test_sqlite_connect_args_defaults() -> None:
    assert DEFAULT_SQLITE_CONNECT_ARGS["check_same_thread"] is False
    assert DEFAULT_SQLITE_CONNECT_ARGS["timeout"] == 30


def test_create_engine_from_config_sqlite_uses_safe_pool() -> None:
    engine = create_engine_from_config("sqlite:///./test_workspace_engine.db")
    try:
        assert engine.pool.__class__ is NullPool
        assert engine.dialect.name == "sqlite"
    finally:
        engine.dispose()


def test_memory_sqlite_uses_static_pool() -> None:
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args=dict(DEFAULT_SQLITE_CONNECT_ARGS),
        poolclass=StaticPool,
        future=True,
    )
    try:
        assert engine.pool.__class__ is StaticPool
    finally:
        engine.dispose()


def test_is_database_locked_error() -> None:
    exc = OperationalError("INSERT", {}, Exception("database is locked"))
    assert is_database_locked_error(exc) is True
    other = OperationalError("INSERT", {}, Exception("no such table"))
    assert is_database_locked_error(other) is False


def test_run_with_sqlite_retry_eventually_succeeds() -> None:
    attempts = {"count": 0}

    def _fn() -> str:
        attempts["count"] += 1
        if attempts["count"] < 3:
            raise OperationalError("INSERT", {}, Exception("database is locked"))
        return "ok"

    assert run_with_sqlite_retry(_fn, max_attempts=3, base_delay=0.0) == "ok"
    assert attempts["count"] == 3
