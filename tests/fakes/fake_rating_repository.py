from decimal import Decimal

from app.domain.feedback.entities import Rating
from app.domain.feedback.repositories import IRatingRepository
from app.domain.shared.types import EntityId


class FakeRatingRepository(IRatingRepository):
    async def __init__(self) -> None:
        self._store: list[Rating] = []

    async def add(self, rating: Rating) -> None:
        self._store.append(rating)

    async def find_by_project(self, project_id: EntityId) -> Rating | None:
        for rating in self._store:
            if rating.project_id == project_id:
                return rating
        return None

    async def list_by_freelancer(self, freelancer_profile_id: EntityId) -> list[Rating]:
        return [r for r in self._store if r.freelancer_profile_id == freelancer_profile_id]

    async def average_score_for_freelancer(
        self, freelancer_profile_id: EntityId
    ) -> Decimal | None:
        scores = [r.score for r in self.list_by_freelancer(freelancer_profile_id)]
        if not scores:
            return None
        return Decimal(sum(scores)) / Decimal(len(scores))
