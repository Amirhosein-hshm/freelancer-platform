from app.domain.category.entities import CategorySupervisor
from app.domain.category.repositories import ICategorySupervisorRepository
from app.domain.shared.types import EntityId


class FakeCategorySupervisorRepository(ICategorySupervisorRepository):
    async def __init__(self) -> None:
        self._store: list[CategorySupervisor] = []

    async def add(self, link: CategorySupervisor) -> None:
        self._store.append(link)

    async def list_active_supervisors(self, category_id: EntityId) -> list[CategorySupervisor]:
        return [
            link
            for link in self._store
            if link.category_id == category_id and link.is_active
        ]

    async def list_categories_for_supervisor(self, supervisor_user_id: EntityId) -> list[EntityId]:
        return [
            link.category_id
            for link in self._store
            if link.supervisor_user_id == supervisor_user_id and link.is_active
        ]

    async def is_supervisor_of(self, supervisor_user_id: EntityId, category_id: EntityId) -> bool:
        return any(
            link.supervisor_user_id == supervisor_user_id
            and link.category_id == category_id
            and link.is_active
            for link in self._store
        )

    async def update(self, link: CategorySupervisor) -> None:
        for i, stored in enumerate(self._store):
            if stored.id == link.id:
                self._store[i] = link
                return
        self._store.append(link)
