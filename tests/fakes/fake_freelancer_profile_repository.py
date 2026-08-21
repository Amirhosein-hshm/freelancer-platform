from app.domain.freelancer.entities import FreelancerProfile
from app.domain.freelancer.enums import FreelancerApprovalStatus
from app.domain.freelancer.exceptions import FreelancerProfileNotFoundError
from app.domain.freelancer.repositories import IFreelancerProfileRepository
from app.domain.shared.types import EntityId


class FakeFreelancerProfileRepository(IFreelancerProfileRepository):
    """Mirrors the SQLAlchemy repository: every read excludes soft-deleted profiles."""

    def __init__(self) -> None:
        self._store: dict[str, FreelancerProfile] = {}
        self._by_user_id: dict[str, FreelancerProfile] = {}

    async def add(self, profile: FreelancerProfile) -> None:
        self._store[profile.id] = profile
        self._by_user_id[profile.user_id] = profile

    async def get_by_id(self, profile_id: EntityId) -> FreelancerProfile:
        profile = self._store.get(profile_id)
        if profile is None or profile.deleted_at is not None:
            raise FreelancerProfileNotFoundError(f"Freelancer profile {profile_id} not found.")
        return profile

    async def get_by_user_id(self, user_id: EntityId) -> FreelancerProfile:
        profile = self._by_user_id.get(user_id)
        if profile is None or profile.deleted_at is not None:
            raise FreelancerProfileNotFoundError(f"No freelancer profile for user {user_id}.")
        return profile

    async def update(self, profile: FreelancerProfile) -> None:
        old = self._store.get(profile.id)
        if old is not None and old.user_id != profile.user_id:
            self._by_user_id.pop(old.user_id, None)
        self._store[profile.id] = profile
        self._by_user_id[profile.user_id] = profile

    async def list_by_approval_status(self, status: FreelancerApprovalStatus) -> list[FreelancerProfile]:
        return [p for p in self._store.values() if p.approval_status == status and p.deleted_at is None]

    async def list_available_for_level(self, level_id: EntityId) -> list[FreelancerProfile]:
        return [
            p
            for p in self._store.values()
            if p.is_approved() and p.is_available and p.current_level_id == level_id and p.deleted_at is None
        ]
