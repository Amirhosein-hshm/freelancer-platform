"""Fixtures for infrastructure integration tests (real Postgres).

Tests in ``tests/infrastructure/`` are marked ``integration`` and run against a
real Postgres test database (never SQLite) per TESTING.md §8. The schema is
rebuilt from ``Base.metadata`` at session start and all tables are truncated
between tests for isolation.

Each test receives its own engine/session factory bound to the test's event
loop (asyncpg connections cannot cross event loops), so no fixture is
session-scoped over the event loop.
"""

import asyncio
import os
from collections.abc import AsyncIterator
from datetime import UTC, datetime

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.infrastructure.db import models  # noqa: F401  (register all ORM models)
from app.infrastructure.db.base import Base

TEST_DATABASE_URL = os.environ.get(
    "TEST_DATABASE_URL",
    "postgresql+asyncpg://app_user:change_me@localhost:5433/freelance_platform_test",
)


def _build_schema() -> None:
    """Create all tables once per session, in a throwaway loop."""
    async def _create() -> None:
        engine = create_async_engine(TEST_DATABASE_URL)
        try:
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.drop_all)
                await conn.run_sync(Base.metadata.create_all)
        finally:
            await engine.dispose()

    asyncio.run(_create())


_build_schema()


async def _make_engine() -> AsyncEngine:
    return create_async_engine(TEST_DATABASE_URL)


@pytest.fixture
async def engine() -> AsyncIterator[AsyncEngine]:
    eng = await _make_engine()
    yield eng
    await eng.dispose()


@pytest.fixture
async def session_factory(engine: AsyncEngine):
    return async_sessionmaker(engine, expire_on_commit=False)


@pytest.fixture
async def db_session(session_factory) -> AsyncIterator[AsyncSession]:
    async with session_factory() as session:
        yield session
        await session.rollback()


@pytest.fixture(autouse=True)
async def _truncate_tables(db_session: AsyncSession) -> None:
    """Wipe all rows between tests so each test starts from an empty stable schema."""
    yield
    await db_session.rollback()
    table_names = ", ".join(f'"{t.name}"' for t in reversed(Base.metadata.sorted_tables))
    await db_session.execute(text(f"TRUNCATE {table_names} RESTART IDENTITY CASCADE"))
    await db_session.commit()


@pytest.fixture
def now() -> datetime:
    return datetime(2026, 8, 2, tzinfo=UTC)