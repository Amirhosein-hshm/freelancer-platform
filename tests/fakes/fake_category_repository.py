from app.domain.category.entities import Category
from app.domain.category.exceptions import CategoryNotFoundError
from app.domain.category.repositories import ICategoryRepository
from app.domain.shared.types import EntityId


class FakeCategoryRepository(ICategoryRepository):
    """Mirrors the SQLAlchemy repository: every read excludes soft-deleted categories."""

    def __init__(self) -> None:
        self._store: dict[str, Category] = {}
        self._by_slug: dict[str, Category] = {}

    async def add(self, category: Category) -> None:
        self._store[category.id] = category
        self._by_slug[category.slug] = category

    async def get_by_id(self, category_id: EntityId) -> Category:
        category = self._store.get(category_id)
        if category is None or category.deleted_at is not None:
            raise CategoryNotFoundError(f"Category {category_id} not found.")
        return category

    async def get_by_slug(self, slug: str) -> Category:
        category = self._by_slug.get(slug)
        if category is None or category.deleted_at is not None:
            raise CategoryNotFoundError(f"Category with slug '{slug}' not found.")
        return category

    async def list_active(self) -> list[Category]:
        return [c for c in self._store.values() if c.is_active and c.deleted_at is None]

    async def list_by_parent_id(self, parent_category_id: EntityId) -> list[Category]:
        return [c for c in self._store.values() if c.parent_category_id == parent_category_id and c.deleted_at is None]

    async def update(self, category: Category) -> None:
        old = self._store.get(category.id)
        if old is not None and old.slug != category.slug:
            self._by_slug.pop(old.slug, None)
        self._store[category.id] = category
        self._by_slug[category.slug] = category
