from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.application.shared.ports import IUnitOfWork


class SqlAlchemyUnitOfWork(IUnitOfWork):
    """Binds the request-scoped :class:`AsyncSession` for the duration of the block.

    The session is injected (the same one every repository in the request receives),
    guaranteeing a single transaction per request: ``commit``/``rollback`` act on the
    shared session, and ``__aexit__`` rolls back on error. The session itself is owned
    by the request-scoped ``get_db_session`` dependency, so it is never closed here.
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    @property
    def session(self) -> AsyncSession:
        return self._session

    async def __aenter__(self) -> "SqlAlchemyUnitOfWork":
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: Any,
    ) -> None:
        if exc_type is not None:
            await self._session.rollback()

    async def commit(self) -> None:
        await self.session.commit()

    async def rollback(self) -> None:
        await self.session.rollback()
