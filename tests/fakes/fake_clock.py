from datetime import UTC, datetime

from app.application.shared.ports import IClock


class FakeClock(IClock):
    def __init__(self, fixed_now: datetime | None = None) -> None:
        self._now = fixed_now if fixed_now is not None else datetime(2026, 8, 2, tzinfo=UTC)
        self.current = self._now

    async def now(self) -> datetime:
        return self.current

    def advance(self, **kwargs: int) -> None:
        self.current = self.current.replace(**kwargs)