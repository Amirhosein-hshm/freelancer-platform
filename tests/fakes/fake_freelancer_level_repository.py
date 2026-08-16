from app.domain.freelancer.entities import FreelancerLevel
from app.domain.freelancer.exceptions import FreelancerLevelNotFoundError
from app.domain.freelancer.repositories import IFreelancerLevelRepository
from app.domain.shared.types import EntityId


class FakeFreelancerLevelRepository(IFreelancerLevelRepository):
    def __init__(self) -> None:
        self._store: dict[str, FreelancerLevel] = {}
        self._by_key: dict[str, FreelancerLevel] = {}

    def _add_sync(self, level: FreelancerLevel) -> None:
        self._store[level.id] = level
        self._by_key[level.level_key] = level

    async def add(self, level: FreelancerLevel) -> None:
        self._add_sync(level)

    async def get_by_id(self, level_id: EntityId) -> FreelancerLevel:
        try:
            return self._store[level_id]
        except KeyError:
            raise FreelancerLevelNotFoundError(f"Freelancer level {level_id} not found.") from None

    async def get_by_key(self, level_key: str) -> FreelancerLevel:
        try:
            return self._by_key[level_key]
        except KeyError:
            raise FreelancerLevelNotFoundError(f"Freelancer level '{level_key}' not found.") from None

    async def list_all(self) -> list[FreelancerLevel]:
        return list(self._store.values())

    async def list_active(self) -> list[FreelancerLevel]:
        return [level for level in self._store.values() if level.is_active]

    async def update(self, level: FreelancerLevel) -> None:
        self._add_sync(level)

    async def delete(self, level_id: EntityId) -> None:
        level = self._store.pop(level_id, None)
        if level is not None:
            self._by_key.pop(level.level_key, None)
