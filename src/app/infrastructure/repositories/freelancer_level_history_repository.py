from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.freelancer.entities import FreelancerLevelHistory
from app.domain.freelancer.repositories import IFreelancerLevelHistoryRepository
from app.domain.shared.types import EntityId
from app.infrastructure.db.models.freelancer_models import FreelancerLevelHistoryModel
from app.infrastructure.repositories.freelancer_mapping import to_domain_freelancer_level_history


class SqlAlchemyFreelancerLevelHistoryRepository(IFreelancerLevelHistoryRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, history: FreelancerLevelHistory) -> None:
        self._session.add(
            FreelancerLevelHistoryModel(
                id=history.id,
                freelancer_profile_id=history.freelancer_profile_id,
                old_level=history.old_level.value if history.old_level else None,
                new_level=history.new_level.value,
                assigned_by_user_id=history.assigned_by_user_id,
                reason=history.reason,
                assigned_at=history.assigned_at,
            )
        )

    async def list_by_profile(
        self,
        profile_id: EntityId,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[FreelancerLevelHistory]:
        stmt = (
            select(FreelancerLevelHistoryModel)
            .where(FreelancerLevelHistoryModel.freelancer_profile_id == profile_id)
            .order_by(FreelancerLevelHistoryModel.assigned_at.desc())
        )
        if limit is not None:
            stmt = stmt.limit(limit).offset(offset or 0)
        result = await self._session.execute(stmt)
        return [to_domain_freelancer_level_history(row) for row in result.scalars().all()]

    async def count_by_profile(self, profile_id: EntityId) -> int:
        result = await self._session.execute(
            select(func.count(FreelancerLevelHistoryModel.id)).where(
                FreelancerLevelHistoryModel.freelancer_profile_id == profile_id,
            )
        )
        return int(result.scalar_one())
