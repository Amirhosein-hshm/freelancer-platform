from app.application.shared.ports import IUnitOfWork


class FakeUnitOfWork(IUnitOfWork):
    def __init__(self) -> None:
        self.committed = False
        self.rollback_called = False
        self.commit_count = 0
        self._active = False

    async def __aenter__(self) -> "FakeUnitOfWork":
        self._active = True
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: object,
    ) -> None:
        self._active = False
        if exc_type is not None:
            await self.rollback()

    async def commit(self) -> None:
        self.committed = True
        self.commit_count += 1

    async def rollback(self) -> None:
        self.rollback_called = True