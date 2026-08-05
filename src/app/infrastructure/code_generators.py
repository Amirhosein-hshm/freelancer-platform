from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.shared.ports import IProjectCodeGenerator, ITicketCodeGenerator
from app.infrastructure.db.models.sequence_models import CodeSequenceModel

_CODE_TEMPLATE = "{prefix}-{year}-{value:03d}"


def _increment_sequence(session: AsyncSession, prefix: str, year: int):
    return (
        pg_insert(CodeSequenceModel)
        .values(year=year, prefix=prefix, last_value=1)
        .on_conflict_do_update(
            index_elements=["year", "prefix"],
            set_={"last_value": CodeSequenceModel.last_value + 1},
        )
        .returning(CodeSequenceModel.last_value)
    )


class SqlSequenceProjectCodeGenerator(IProjectCodeGenerator):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def next_code(self, year: int) -> str:
        result = await self._session.execute(_increment_sequence(self._session, "PRJ", year))
        value = result.scalar_one()
        return _CODE_TEMPLATE.format(prefix="PRJ", year=year, value=value)


class SqlSequenceTicketCodeGenerator(ITicketCodeGenerator):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def next_code(self, year: int) -> str:
        result = await self._session.execute(_increment_sequence(self._session, "TCK", year))
        value = result.scalar_one()
        return _CODE_TEMPLATE.format(prefix="TCK", year=year, value=value)