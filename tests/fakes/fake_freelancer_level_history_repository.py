from app.domain.freelancer.entities import FreelancerLevelHistory
from app.domain.freelancer.repositories import IFreelancerLevelHistoryRepository
from app.domain.shared.types import EntityId


class FakeFreelancerLevelHistoryRepository(IFreelancerLevelHistoryRepository):
    def __init__(self) -> None:
        self._store: list[FreelancerLevelHistory] = []

    def add(self, history: FreelancerLevelHistory) -> None:
        self._store.append(history)

    def list_by_profile(self, profile_id: EntityId) -> list[FreelancerLevelHistory]:
        return [h for h in self._store if h.freelancer_profile_id == profile_id]
