"""Atomic project/ticket code generator integration test.

Per TESTING.md §8 the code generator must produce sequential, non-colliding
codes under concurrent calls. Each coroutine uses its own session (asyncpg does
not allow sharing a single session across concurrent tasks), while the atomic
``INSERT ... ON CONFLICT DO UPDATE ... RETURNING`` guarantees unique values.
"""

import asyncio

import pytest
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker

from app.infrastructure.code_generators import (
    SqlSequenceProjectCodeGenerator,
    SqlSequenceTicketCodeGenerator,
)

pytestmark = pytest.mark.integration


async def _one_code(engine: AsyncEngine, amount: int, kind: str) -> str:
    factory = async_sessionmaker(engine, expire_on_commit=False)
    async with factory() as session:
        generator: SqlSequenceProjectCodeGenerator | SqlSequenceTicketCodeGenerator
        if kind == "project":
            generator = SqlSequenceProjectCodeGenerator(session)
        else:
            generator = SqlSequenceTicketCodeGenerator(session)
        code = await generator.next_code(2026)
        await session.commit()
        return code


async def test_project_codes_sequential_and_unique(engine: AsyncEngine) -> None:
    codes = await asyncio.gather(*[_one_code(engine, 1, "project") for _ in range(20)])
    assert len(set(codes)) == 20
    values = [int(c.rsplit("-", 1)[1]) for c in codes]
    assert set(values) == set(range(1, 21))


async def test_ticket_codes_sequential_and_unique(engine: AsyncEngine) -> None:
    codes = await asyncio.gather(*[_one_code(engine, 1, "ticket") for _ in range(20)])
    assert len(set(codes)) == 20
    values = [int(c.rsplit("-", 1)[1]) for c in codes]
    assert set(values) == set(range(1, 21))


async def test_project_and_ticket_prefixes_are_isolated(engine: AsyncEngine) -> None:
    project_codes = await asyncio.gather(*[_one_code(engine, 1, "project") for _ in range(5)])
    ticket_codes = await asyncio.gather(*[_one_code(engine, 1, "ticket") for _ in range(5)])
    assert all(c.startswith("PRJ-") for c in project_codes)
    assert all(c.startswith("TCK-") for c in ticket_codes)
