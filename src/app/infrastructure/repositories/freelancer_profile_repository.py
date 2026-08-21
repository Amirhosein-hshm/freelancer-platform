from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.freelancer.entities import FreelancerProfile
from app.domain.freelancer.enums import FreelancerApprovalStatus, FreelancerLevelEnum
from app.domain.freelancer.exceptions import FreelancerProfileNotFoundError
from app.domain.freelancer.repositories import IFreelancerProfileRepository
from app.domain.shared.types import EntityId
from app.infrastructure.db.models.freelancer_models import FreelancerProfileModel
from app.infrastructure.repositories.freelancer_mapping import to_domain_freelancer_profile


class SqlAlchemyFreelancerProfileRepository(IFreelancerProfileRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, profile: FreelancerProfile) -> None:
        self._session.add(
            FreelancerProfileModel(
                id=profile.id,
                user_id=profile.user_id,
                current_level=profile.current_level.value if profile.current_level else None,
                approval_status=profile.approval_status.value,
                approved_by_user_id=profile.approved_by_user_id,
                approved_at=profile.approved_at,
                approval_note=profile.approval_note,
                display_name=profile.display_name,
                headline=profile.headline,
                bio=profile.bio,
                country_code=profile.country_code,
                city=profile.city,
                timezone=profile.timezone,
                hourly_rate_min=profile.hourly_rate_min,
                hourly_rate_max=profile.hourly_rate_max,
                is_available=profile.is_available,
                deleted_at=profile.deleted_at,
                created_by_user_id=profile.created_by_user_id,
            )
        )

    async def get_by_id(self, profile_id: EntityId) -> FreelancerProfile:
        result = await self._session.execute(
            select(FreelancerProfileModel).where(
                FreelancerProfileModel.id == profile_id,
                FreelancerProfileModel.deleted_at.is_(None),
            )
        )
        row = result.scalar_one_or_none()
        if row is None:
            raise FreelancerProfileNotFoundError(f"Freelancer profile {profile_id} not found.")
        return to_domain_freelancer_profile(row)

    async def get_by_user_id(self, user_id: EntityId) -> FreelancerProfile:
        result = await self._session.execute(
            select(FreelancerProfileModel).where(
                FreelancerProfileModel.user_id == user_id,
                FreelancerProfileModel.deleted_at.is_(None),
            )
        )
        row = result.scalar_one_or_none()
        if row is None:
            raise FreelancerProfileNotFoundError(f"Freelancer profile for user {user_id} not found.")
        return to_domain_freelancer_profile(row)

    async def update(self, profile: FreelancerProfile) -> None:
        row = await self._session.get(FreelancerProfileModel, profile.id)
        if row is None:
            raise FreelancerProfileNotFoundError(f"Freelancer profile {profile.id} not found.")
        row.current_level = profile.current_level.value if profile.current_level else None
        row.approval_status = profile.approval_status.value
        row.approved_by_user_id = profile.approved_by_user_id
        row.approved_at = profile.approved_at
        row.approval_note = profile.approval_note
        row.display_name = profile.display_name
        row.headline = profile.headline
        row.bio = profile.bio
        row.country_code = profile.country_code
        row.city = profile.city
        row.timezone = profile.timezone
        row.hourly_rate_min = profile.hourly_rate_min
        row.hourly_rate_max = profile.hourly_rate_max
        row.is_available = profile.is_available
        row.deleted_at = profile.deleted_at
        row.created_by_user_id = profile.created_by_user_id

    async def list_by_approval_status(
        self,
        status: FreelancerApprovalStatus,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[FreelancerProfile]:
        stmt = (
            select(FreelancerProfileModel)
            .where(
                FreelancerProfileModel.approval_status == status.value,
                FreelancerProfileModel.deleted_at.is_(None),
            )
            .order_by(FreelancerProfileModel.created_at.desc())
        )
        if limit is not None:
            stmt = stmt.limit(limit).offset(offset or 0)
        result = await self._session.execute(stmt)
        return [to_domain_freelancer_profile(row) for row in result.scalars().all()]

    async def count_by_approval_status(self, status: FreelancerApprovalStatus) -> int:
        result = await self._session.execute(
            select(func.count(FreelancerProfileModel.id)).where(
                FreelancerProfileModel.approval_status == status.value,
                FreelancerProfileModel.deleted_at.is_(None),
            )
        )
        return int(result.scalar_one())

    async def list_available_for_level(self, level: FreelancerLevelEnum) -> list[FreelancerProfile]:
        result = await self._session.execute(
            select(FreelancerProfileModel)
            .where(
                FreelancerProfileModel.current_level == level.value,
                FreelancerProfileModel.is_available.is_(True),
                FreelancerProfileModel.deleted_at.is_(None),
            )
            .order_by(FreelancerProfileModel.created_at.desc())
        )
        return [to_domain_freelancer_profile(row) for row in result.scalars().all()]
