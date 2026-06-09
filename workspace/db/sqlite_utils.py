"""SQLite-specific helpers for workspace database access."""

from __future__ import annotations

import time
from collections.abc import Callable
from typing import TypeVar

from sqlalchemy.exc import OperationalError

T = TypeVar("T")

DEFAULT_SQLITE_CONNECT_ARGS = {"check_same_thread": False, "timeout": 30}


def is_database_locked_error(exc: BaseException) -> bool:
    return isinstance(exc, OperationalError) and "database is locked" in str(exc).lower()


def run_with_sqlite_retry(
    fn: Callable[[], T],
    *,
    max_attempts: int = 3,
    base_delay: float = 0.05,
) -> T:
    """Retry SQLite writes when the database is temporarily locked."""
    last_exc: OperationalError | None = None
    for attempt in range(max_attempts):
        try:
            return fn()
        except OperationalError as exc:
            if not is_database_locked_error(exc):
                raise
            last_exc = exc
            if attempt >= max_attempts - 1:
                raise
            time.sleep(base_delay * (2**attempt))
    assert last_exc is not None
    raise last_exc
