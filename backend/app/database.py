"""Database engine and session management (SQLModel / SQLAlchemy 2)."""
from __future__ import annotations

from collections.abc import Generator

from sqlmodel import Session, SQLModel, create_engine

from app.config import get_settings

settings = get_settings()


def _normalize_url(url: str) -> str:
    # Managed Postgres (Render/Railway/Heroku) hands out `postgres://` /
    # `postgresql://` URLs; pin them to the psycopg3 driver we install.
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql+psycopg://", 1)
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+psycopg://", 1)
    return url


_database_url = _normalize_url(settings.database_url)

# SQLite (handy for keyless local dev) needs check_same_thread disabled so the
# chat SSE generator can open a session on a worker thread. Postgres uses
# pool_pre_ping to survive dropped connections.
_is_sqlite = _database_url.startswith("sqlite")
_engine_kwargs: dict = (
    {"connect_args": {"check_same_thread": False}}
    if _is_sqlite
    else {"pool_pre_ping": True}
)

# echo=False keeps logs clean; flip to True when debugging SQL.
engine = create_engine(_database_url, echo=False, **_engine_kwargs)


def init_db() -> None:
    """Create tables. In production prefer Alembic migrations; this is fine for
    a portfolio project and for the test suite (SQLite in-memory)."""
    # Import models so they register on SQLModel.metadata before create_all.
    from app import models  # noqa: F401

    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session
