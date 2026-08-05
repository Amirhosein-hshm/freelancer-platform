from app.domain.category.entities import Category
from app.domain.category.exceptions import CategoryNotFoundError
from app.domain.category.repositories import ICategoryRepository
from app.domain.shared.types import EntityId


class FakeCategoryRepository(ICategoryRepository):
    def __init__(self) -> None:
        self._store: dict[str, Category] = {}
        self._by_slug: dict[str, Category] = {}

    async def add(self, category: Category) -> None:
        self._store[category.id] = category
        self._by_slug[category.slug] = category

    async def get_by_id(self, category_id: EntityId) -> Category:
        try:
            return self._store[category_id]
        except KeyError:
            raise CategoryNotFoundError(f"Category {category_id} not found.") from None

    async def get_by_slug(self, slug: str) -> Category:
        try:
            return self._by_slug[slug]
        except KeyError:
            raise CategoryNotFoundError(f"Category with slug '{slug}' not found.") from None

    async def list_active(self) -> list[Category]:
        return [c for c in self._store.values() if c.is_active and c.deleted_at is None]

    async def update(self, category: Category) -> None:
        old = self._store.get(category.id)
        if old is not None and old.slug != category.slug:
            self._by_slug.pop(old.slug, None)
        self._store[category.id] = category
        self._by_slug[category.slug] = category
