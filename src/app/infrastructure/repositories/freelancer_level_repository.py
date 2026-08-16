from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.freelancer.entities import FreelancerLevel
from app.domain.freelancer.exceptions import FreelancerLevelNotFoundError
from app.domain.freelancer.repositories import IFreelancerLevelRepository
from app.domain.shared.types import EntityId
from app.infrastructure.db.models.freelancer_models import FreelancerLevelModel
from app.infrastructure.repositories.freelancer_mapping import to_domain_freelancer_level


class SqlAlchemyFreelancerLevelRepository(IFreelancerLevelRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, level_id: EntityId) -> FreelancerLevel:
        row = await self._session.get(FreelancerLevelModel, level_id)
        if row is None:
            raise FreelancerLevelNotFoundError(f"Freelancer level {level_id} not found.")
        return to_domain_freelancer_level(row)

    async def get_by_key(self, level_key: str) -> FreelancerLevel:
        result = await self._session.execute(
            select(FreelancerLevelModel).where(FreelancerLevelModel.level_key == level_key)
        )
        row = result.scalar_one_or_none()
        if row is None:
            raise FreelancerLevelNotFoundError(f"Freelancer level '{level_key}' not found.")
        return to_domain_freelancer_level(row)

    async def list_active(self) -> list[FreelancerLevel]:
        result = await self._session.execute(
            select(FreelancerLevelModel)
            .where(FreelancerLevelModel.is_active.is_(True))
            .order_by(FreelancerLevelModel.rank_order.asc())
        )
        return [to_domain_freelancer_level(row) for row in result.scalars().all()]
