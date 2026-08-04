from app.domain.review.entities import SupervisorReview
from app.domain.review.enums import ReviewStatus
from app.domain.review.exceptions import SupervisorReviewNotFoundError
from app.domain.review.repositories import ISupervisorReviewRepository
from app.domain.shared.types import EntityId


class FakeSupervisorReviewRepository(ISupervisorReviewRepository):
    async def __init__(self) -> None:
        self._store: dict[str, SupervisorReview] = {}

    async def add(self, review: SupervisorReview) -> None:
        self._store[review.id] = review

    async def get_by_delivery(self, project_delivery_id: EntityId) -> SupervisorReview:
        for review in self._store.values():
            if review.project_delivery_id == project_delivery_id:
                return review
        raise SupervisorReviewNotFoundError(
            f"No review for delivery {project_delivery_id}."
        )

    async def find_by_delivery(self, project_delivery_id: EntityId) -> SupervisorReview | None:
        for review in self._store.values():
            if review.project_delivery_id == project_delivery_id:
                return review
        return None

    async def list_pending_for_supervisor(
        self, supervisor_user_id: EntityId
    ) -> list[SupervisorReview]:
        return [
            review
            for review in self._store.values()
            if review.supervisor_user_id == supervisor_user_id
            and review.decision == ReviewStatus.PENDING
        ]

    async def update(self, review: SupervisorReview) -> None:
        self._store[review.id] = review
