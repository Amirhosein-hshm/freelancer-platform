from app.domain.feedback.entities import CustomerReview
from app.domain.feedback.repositories import ICustomerReviewRepository
from app.domain.shared.types import EntityId


class FakeCustomerReviewRepository(ICustomerReviewRepository):
    def __init__(self) -> None:
        self._store: dict[str, CustomerReview] = {}

    async def add(self, review: CustomerReview) -> None:
        self._store[review.id] = review

    async def find_by_project(self, project_id: EntityId) -> CustomerReview | None:
        for review in self._store.values():
            if review.project_id == project_id:
                return review
        return None
