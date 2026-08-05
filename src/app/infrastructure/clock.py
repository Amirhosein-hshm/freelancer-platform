from datetime import UTC, datetime

from app.application.shared.ports import IClock


class SystemClock(IClock):
    async def now(self) -> datetime:
        return datetime.now(UTC)