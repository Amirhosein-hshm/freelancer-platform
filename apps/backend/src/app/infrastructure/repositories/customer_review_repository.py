from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.feedback.entities import CustomerReview
from app.domain.feedback.exceptions import CustomerReviewNotFoundError
from app.domain.feedback.repositories import ICustomerReviewRepository
from app.domain.shared.types import EntityId
from app.infrastructure.db.models.feedback_models import CustomerReviewModel
from app.infrastructure.repositories.feedback_mapping import to_domain_customer_review


class SqlAlchemyCustomerReviewRepository(ICustomerReviewRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, review: CustomerReview) -> None:
        self._session.add(
            CustomerReviewModel(
                id=review.id,
                project_id=review.project_id,
                project_delivery_id=review.project_delivery_id,
                customer_user_id=review.customer_user_id,
                decision=review.decision.value,
                comment=review.comment,
                reviewed_at=review.reviewed_at,
                created_at=review.created_at,
            )
        )

    async def get_by_id(self, review_id: EntityId) -> CustomerReview:
        row = await self._session.get(CustomerReviewModel, review_id)
        if row is None:
            raise CustomerReviewNotFoundError(f"Customer review {review_id} not found.")
        return to_domain_customer_review(row)

    async def find_by_project(self, project_id: EntityId) -> CustomerReview | None:
        result = await self._session.execute(
            select(CustomerReviewModel)
            .where(CustomerReviewModel.project_id == project_id)
            .order_by(CustomerReviewModel.reviewed_at.desc())
        )
        row = result.scalar_one_or_none()
        return to_domain_customer_review(row) if row is not None else None

    async def list_by_project(self, project_id: EntityId) -> list[CustomerReview]:
        result = await self._session.execute(
            select(CustomerReviewModel)
            .where(CustomerReviewModel.project_id == project_id)
            .order_by(CustomerReviewModel.reviewed_at.desc())
        )
        return [to_domain_customer_review(row) for row in result.scalars().all()]

    async def update(self, review: CustomerReview) -> None:
        row = await self._session.get(CustomerReviewModel, review.id)
        if row is None:
            raise CustomerReviewNotFoundError(f"Customer review {review.id} not found.")
        row.project_id = review.project_id
        row.project_delivery_id = review.project_delivery_id
        row.customer_user_id = review.customer_user_id
        row.decision = review.decision.value
        row.comment = review.comment
        row.reviewed_at = review.reviewed_at

    async def delete(self, review_id: EntityId) -> None:
        row = await self._session.get(CustomerReviewModel, review_id)
        if row is not None:
            await self._session.delete(row)
