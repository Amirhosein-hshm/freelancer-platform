from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.review.entities import SupervisorReview
from app.domain.review.enums import ReviewStatus
from app.domain.review.exceptions import SupervisorReviewNotFoundError
from app.domain.review.repositories import ISupervisorReviewRepository
from app.domain.shared.types import EntityId
from app.infrastructure.db.models.review_models import SupervisorReviewModel
from app.infrastructure.repositories.review_mapping import to_domain_supervisor_review


class SqlAlchemySupervisorReviewRepository(ISupervisorReviewRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, review: SupervisorReview) -> None:
        self._session.add(
            SupervisorReviewModel(
                id=review.id,
                project_delivery_id=review.project_delivery_id,
                project_id=review.project_id,
                supervisor_user_id=review.supervisor_user_id,
                decision=review.decision.value,
                reject_reason=review.reject_reason,
                notes=review.notes,
                reviewed_at=review.reviewed_at,
            )
        )

    async def get_by_delivery(self, project_delivery_id: EntityId) -> SupervisorReview:
        row = await self._find_row_by_delivery(project_delivery_id)
        if row is None:
            raise SupervisorReviewNotFoundError(f"Supervisor review for delivery {project_delivery_id} not found.")
        return to_domain_supervisor_review(row)

    async def find_by_delivery(self, project_delivery_id: EntityId) -> SupervisorReview | None:
        row = await self._find_row_by_delivery(project_delivery_id)
        return to_domain_supervisor_review(row) if row is not None else None

    async def list_pending_for_supervisor(
        self,
        supervisor_user_id: EntityId,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[SupervisorReview]:
        stmt = (
            select(SupervisorReviewModel)
            .where(
                SupervisorReviewModel.supervisor_user_id == supervisor_user_id,
                SupervisorReviewModel.decision == ReviewStatus.PENDING.value,
            )
            .order_by(SupervisorReviewModel.created_at.desc())
        )
        if limit is not None:
            stmt = stmt.limit(limit).offset(offset or 0)
        result = await self._session.execute(stmt)
        return [to_domain_supervisor_review(row) for row in result.scalars().all()]

    async def count_pending_for_supervisor(self, supervisor_user_id: EntityId) -> int:
        result = await self._session.execute(
            select(func.count(SupervisorReviewModel.id)).where(
                SupervisorReviewModel.supervisor_user_id == supervisor_user_id,
                SupervisorReviewModel.decision == ReviewStatus.PENDING.value,
            )
        )
        return int(result.scalar_one())

    async def update(self, review: SupervisorReview) -> None:
        row = await self._session.get(SupervisorReviewModel, review.id)
        if row is None:
            raise SupervisorReviewNotFoundError(f"Supervisor review {review.id} not found.")
        row.project_delivery_id = review.project_delivery_id
        row.project_id = review.project_id
        row.supervisor_user_id = review.supervisor_user_id
        row.decision = review.decision.value
        row.reject_reason = review.reject_reason
        row.notes = review.notes
        row.reviewed_at = review.reviewed_at

    async def _find_row_by_delivery(self, project_delivery_id: EntityId) -> SupervisorReviewModel | None:
        result = await self._session.execute(
            select(SupervisorReviewModel).where(SupervisorReviewModel.project_delivery_id == project_delivery_id)
        )
        return result.scalar_one_or_none()
