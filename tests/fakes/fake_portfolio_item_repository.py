from app.domain.freelancer.entities import PortfolioItem
from app.domain.freelancer.exceptions import PortfolioItemNotFoundError
from app.domain.freelancer.repositories import IPortfolioItemRepository
from app.domain.shared.types import EntityId


class FakePortfolioItemRepository(IPortfolioItemRepository):
    def __init__(self) -> None:
        self._store: dict[str, PortfolioItem] = {}

    async def add(self, item: PortfolioItem) -> None:
        self._store[item.id] = item

    async def get_by_id(self, item_id: EntityId) -> PortfolioItem:
        try:
            return self._store[item_id]
        except KeyError:
            raise PortfolioItemNotFoundError(f"Portfolio item {item_id} not found.") from None

    async def list_by_profile(self, profile_id: EntityId) -> list[PortfolioItem]:
        return [i for i in self._store.values() if i.freelancer_profile_id == profile_id]

    async def get_by_file_asset_id(self, file_asset_id: EntityId) -> PortfolioItem | None:
        for item in self._store.values():
            if item.file_asset_id == file_asset_id:
                return item
        return None

    async def update(self, item: PortfolioItem) -> None:
        self._store[item.id] = item

    async def delete(self, item_id: EntityId) -> None:
        self._store.pop(item_id, None)
