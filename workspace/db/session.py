"""SQLAlchemy engine and session factory for the workspace database."""

from __future__ import annotations

from collections.abc import Generator
from contextlib import contextmanager

from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import NullPool, StaticPool

from workspace.config import WORKSPACE_DATABASE_URL
from workspace.db.models import Base
from workspace.db.sqlite_utils import DEFAULT_SQLITE_CONNECT_ARGS


def _is_sqlite_url(url: str) -> bool:
    return url.startswith("sqlite")


def create_engine_from_config(database_url: str | None = None, *, echo: bool = False) -> Engine:
    """Create a SQLAlchemy engine from config or an explicit URL."""
    url = database_url or WORKSPACE_DATABASE_URL
    if not url:
        raise ValueError(
            "WORKSPACE_DATABASE_URL is not set. "
            "Set it in the environment before enabling the workspace layer."
        )

    engine_kwargs: dict = {"echo": echo, "future": True, "pool_pre_ping": True}

    if _is_sqlite_url(url):
        engine_kwargs["connect_args"] = dict(DEFAULT_SQLITE_CONNECT_ARGS)
        if ":memory:" in url or url.rstrip("/").endswith(":memory:"):
            engine_kwargs["poolclass"] = StaticPool
        else:
            engine_kwargs["poolclass"] = NullPool

    engine = create_engine(url, **engine_kwargs)

    if _is_sqlite_url(url):

        @event.listens_for(engine, "connect")
        def _set_sqlite_pragmas(dbapi_connection, _connection_record) -> None:
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA journal_mode=WAL")
            cursor.execute("PRAGMA busy_timeout=30000")
            cursor.close()

    return engine


def get_session_factory(engine: Engine) -> sessionmaker[Session]:
    """Return a session factory bound to the given engine."""
    return sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)


def init_db(engine: Engine) -> None:
    """Create all workspace tables (used in tests and local bootstrap)."""
    Base.metadata.create_all(bind=engine)


@contextmanager
def session_scope(session_factory: sessionmaker[Session]) -> Generator[Session, None, None]:
    """Provide a transactional scope around a series of operations."""
    session = session_factory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
