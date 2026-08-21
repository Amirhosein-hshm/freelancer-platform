from app.domain.freelancer.entities import PortfolioItem
from app.domain.freelancer.exceptions import PortfolioItemNotFoundError
from app.domain.freelancer.repositories import IPortfolioItemRepository
from app.domain.shared.types import EntityId


class FakePortfolioItemRepository(IPortfolioItemRepository):
    """Mirrors the SQLAlchemy repository: every read excludes soft-deleted items."""

    def __init__(self) -> None:
        self._store: dict[str, PortfolioItem] = {}

    async def add(self, item: PortfolioItem) -> None:
        self._store[item.id] = item

    async def get_by_id(self, item_id: EntityId) -> PortfolioItem:
        item = self._store.get(item_id)
        if item is None or item.deleted_at is not None:
            raise PortfolioItemNotFoundError(f"Portfolio item {item_id} not found.")
        return item

    async def list_by_profile(self, profile_id: EntityId) -> list[PortfolioItem]:
        return [
            i for i in self._store.values() if i.freelancer_profile_id == profile_id and i.deleted_at is None
        ]

    async def get_by_file_asset_id(self, file_asset_id: EntityId) -> PortfolioItem | None:
        for item in self._store.values():
            if item.file_asset_id == file_asset_id and item.deleted_at is None:
                return item
        return None

    async def update(self, item: PortfolioItem) -> None:
        self._store[item.id] = item
