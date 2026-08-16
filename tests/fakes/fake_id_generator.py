from app.application.shared.ports import IIdGenerator
from app.domain.shared.types import EntityId


class FakeIdGenerator(IIdGenerator):
    def __init__(self, prefix: str = "id") -> None:
        self._prefix = prefix
        self._counter = 0
        self.generated: list[str] = []

    async def new_id(self) -> EntityId:
        self._counter += 1
        value = f"{self._prefix}-{self._counter}"
        self.generated.append(value)
        return value
