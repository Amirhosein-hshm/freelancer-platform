from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.category.entities import Category
from app.domain.category.exceptions import CategoryNotFoundError
from app.domain.category.repositories import ICategoryRepository
from app.domain.shared.types import EntityId
from app.infrastructure.db.models.category_models import CategoryModel
from app.infrastructure.repositories.category_mapping import to_domain_category


class SqlAlchemyCategoryRepository(ICategoryRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, category: Category) -> None:
        self._session.add(
            CategoryModel(
                id=category.id,
                parent_category_id=category.parent_category_id,
                category_key=category.category_key,
                name=category.name,
                slug=category.slug,
                description=category.description,
                is_active=category.is_active,
                sort_order=category.sort_order,
                deleted_at=category.deleted_at,
            )
        )

    async def get_by_id(self, category_id: EntityId) -> Category:
        result = await self._session.execute(
            select(CategoryModel).where(CategoryModel.id == category_id, CategoryModel.deleted_at.is_(None))
        )
        row = result.scalar_one_or_none()
        if row is None:
            raise CategoryNotFoundError(f"Category {category_id} not found.")
        return to_domain_category(row)

    async def get_by_slug(self, slug: str) -> Category:
        result = await self._session.execute(
            select(CategoryModel).where(CategoryModel.slug == slug, CategoryModel.deleted_at.is_(None))
        )
        row = result.scalar_one_or_none()
        if row is None:
            raise CategoryNotFoundError(f"Category with slug '{slug}' not found.")
        return to_domain_category(row)

    async def list_active(
        self,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[Category]:
        stmt = (
            select(CategoryModel)
            .where(
                CategoryModel.is_active.is_(True),
                CategoryModel.deleted_at.is_(None),
            )
            .order_by(CategoryModel.sort_order.asc())
        )
        if limit is not None:
            stmt = stmt.limit(limit).offset(offset or 0)
        result = await self._session.execute(stmt)
        return [to_domain_category(row) for row in result.scalars().all()]

    async def count_active(self) -> int:
        result = await self._session.execute(
            select(func.count(CategoryModel.id)).where(
                CategoryModel.is_active.is_(True),
                CategoryModel.deleted_at.is_(None),
            )
        )
        return int(result.scalar_one())

    async def list_by_parent_id(self, parent_category_id: EntityId) -> list[Category]:
        result = await self._session.execute(
            select(CategoryModel)
            .where(
                CategoryModel.parent_category_id == parent_category_id,
                CategoryModel.deleted_at.is_(None),
            )
            .order_by(CategoryModel.sort_order.asc())
        )
        return [to_domain_category(row) for row in result.scalars().all()]

    async def update(self, category: Category) -> None:
        row = await self._session.get(CategoryModel, category.id)
        if row is None:
            raise CategoryNotFoundError(f"Category {category.id} not found.")
        row.parent_category_id = category.parent_category_id
        row.category_key = category.category_key
        row.name = category.name
        row.slug = category.slug
        row.description = category.description
        row.is_active = category.is_active
        row.sort_order = category.sort_order
        row.deleted_at = category.deleted_at
