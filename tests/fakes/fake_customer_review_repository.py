from app.domain.feedback.entities import CustomerReview
from app.domain.feedback.exceptions import CustomerReviewNotFoundError
from app.domain.feedback.repositories import ICustomerReviewRepository
from app.domain.shared.types import EntityId


class FakeCustomerReviewRepository(ICustomerReviewRepository):
    def __init__(self) -> None:
        self._store: dict[str, CustomerReview] = {}

    async def add(self, review: CustomerReview) -> None:
        self._store[review.id] = review

    async def get_by_id(self, review_id: EntityId) -> CustomerReview:
        review = self._store.get(review_id)
        if review is None:
            raise CustomerReviewNotFoundError(f"Customer review {review_id} not found.")
        return review

    async def find_by_project(self, project_id: EntityId) -> CustomerReview | None:
        for review in self._store.values():
            if review.project_id == project_id:
                return review
        return None

    async def list_by_project(self, project_id: EntityId) -> list[CustomerReview]:
        return sorted(
            (r for r in self._store.values() if r.project_id == project_id),
            key=lambda r: r.reviewed_at,
            reverse=True,
        )

    async def update(self, review: CustomerReview) -> None:
        self._store[review.id] = review

    async def delete(self, review_id: EntityId) -> None:
        self._store.pop(review_id, None)
