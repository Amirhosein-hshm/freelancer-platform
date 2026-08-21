from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.freelancer.entities import PortfolioItem
from app.domain.freelancer.exceptions import PortfolioItemNotFoundError
from app.domain.freelancer.repositories import IPortfolioItemRepository
from app.domain.shared.types import EntityId
from app.infrastructure.db.models.freelancer_models import PortfolioItemModel
from app.infrastructure.repositories.freelancer_mapping import to_domain_portfolio_item


class SqlAlchemyPortfolioItemRepository(IPortfolioItemRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, item: PortfolioItem) -> None:
        self._session.add(
            PortfolioItemModel(
                id=item.id,
                freelancer_profile_id=item.freelancer_profile_id,
                title=item.title,
                description=item.description,
                external_url=item.external_url,
                file_asset_id=item.file_asset_id,
                display_order=item.display_order,
                is_featured=item.is_featured,
                deleted_at=item.deleted_at,
            )
        )

    async def get_by_id(self, item_id: EntityId) -> PortfolioItem:
        result = await self._session.execute(
            select(PortfolioItemModel).where(
                PortfolioItemModel.id == item_id,
                PortfolioItemModel.deleted_at.is_(None),
            )
        )
        row = result.scalar_one_or_none()
        if row is None:
            raise PortfolioItemNotFoundError(f"Portfolio item {item_id} not found.")
        return to_domain_portfolio_item(row)

    async def list_by_profile(
        self,
        profile_id: EntityId,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[PortfolioItem]:
        stmt = (
            select(PortfolioItemModel)
            .where(
                PortfolioItemModel.freelancer_profile_id == profile_id,
                PortfolioItemModel.deleted_at.is_(None),
            )
            .order_by(PortfolioItemModel.display_order.asc())
        )
        if limit is not None:
            stmt = stmt.limit(limit).offset(offset or 0)
        result = await self._session.execute(stmt)
        return [to_domain_portfolio_item(row) for row in result.scalars().all()]

    async def count_by_profile(self, profile_id: EntityId) -> int:
        result = await self._session.execute(
            select(func.count(PortfolioItemModel.id)).where(
                PortfolioItemModel.freelancer_profile_id == profile_id,
                PortfolioItemModel.deleted_at.is_(None),
            )
        )
        return int(result.scalar_one())

    async def get_by_file_asset_id(self, file_asset_id: EntityId) -> PortfolioItem | None:
        result = await self._session.execute(
            select(PortfolioItemModel)
            .where(
                PortfolioItemModel.file_asset_id == file_asset_id,
                PortfolioItemModel.deleted_at.is_(None),
            )
            .limit(1)
        )
        row = result.scalar_one_or_none()
        return to_domain_portfolio_item(row) if row is not None else None

    async def update(self, item: PortfolioItem) -> None:
        row = await self._session.get(PortfolioItemModel, item.id)
        if row is None:
            raise PortfolioItemNotFoundError(f"Portfolio item {item.id} not found.")
        row.title = item.title
        row.description = item.description
        row.external_url = item.external_url
        row.file_asset_id = item.file_asset_id
        row.display_order = item.display_order
        row.is_featured = item.is_featured
        row.deleted_at = item.deleted_at
