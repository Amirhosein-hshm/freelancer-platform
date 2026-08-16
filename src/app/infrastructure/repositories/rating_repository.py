from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.feedback.entities import Rating
from app.domain.feedback.repositories import IRatingRepository
from app.domain.shared.types import EntityId
from app.infrastructure.db.models.feedback_models import RatingModel
from app.infrastructure.repositories.feedback_mapping import to_domain_rating


class SqlAlchemyRatingRepository(IRatingRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, rating: Rating) -> None:
        self._session.add(
            RatingModel(
                id=rating.id,
                customer_review_id=rating.customer_review_id,
                project_id=rating.project_id,
                customer_user_id=rating.customer_user_id,
                freelancer_profile_id=rating.freelancer_profile_id,
                score=rating.score,
                comment=rating.comment,
                is_public=rating.is_public,
                created_at=rating.created_at,
            )
        )

    async def find_by_project(self, project_id: EntityId) -> Rating | None:
        result = await self._session.execute(select(RatingModel).where(RatingModel.project_id == project_id))
        row = result.scalar_one_or_none()
        return to_domain_rating(row) if row is not None else None

    async def list_by_freelancer(self, freelancer_profile_id: EntityId) -> list[Rating]:
        result = await self._session.execute(
            select(RatingModel)
            .where(RatingModel.freelancer_profile_id == freelancer_profile_id)
            .order_by(RatingModel.created_at.desc())
        )
        return [to_domain_rating(row) for row in result.scalars().all()]

    async def average_score_for_freelancer(self, freelancer_profile_id: EntityId) -> Decimal | None:
        result = await self._session.execute(
            select(func.avg(RatingModel.score)).where(RatingModel.freelancer_profile_id == freelancer_profile_id)
        )
        return result.scalar_one_or_none()
