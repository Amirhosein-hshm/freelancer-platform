from app.application.freelancer.dto import (
    FreelancerProfileResult,
    UpdateFreelancerProfileCommand,
)
from app.application.shared.use_case import UseCase
from app.domain.freelancer.entities import FreelancerProfile
from app.domain.freelancer.repositories import IFreelancerProfileRepository


def to_profile_result(profile: FreelancerProfile) -> FreelancerProfileResult:
    return FreelancerProfileResult(
        profile_id=profile.id,
        user_id=profile.user_id,
        display_name=profile.display_name,
        headline=profile.headline,
        bio=profile.bio,
        country_code=profile.country_code,
        city=profile.city,
        timezone=profile.timezone,
        hourly_rate_min=profile.hourly_rate_min,
        hourly_rate_max=profile.hourly_rate_max,
        is_available=profile.is_available,
        current_level_id=profile.current_level_id,
        approval_status=profile.approval_status,
        approved_at=profile.approved_at,
    )


class UpdateFreelancerProfileUseCase(UseCase[UpdateFreelancerProfileCommand, FreelancerProfileResult]):
    def __init__(
        self,
        profile_repo: IFreelancerProfileRepository,
    ) -> None:
        self._profile_repo = profile_repo

    async def execute(self, request: UpdateFreelancerProfileCommand) -> FreelancerProfileResult:
        request.validate()
        profile = await self._profile_repo.get_by_user_id(request.user_id)
        if request.display_name is not None:
            profile.display_name = request.display_name
        if request.headline is not None:
            profile.headline = request.headline
        if request.bio is not None:
            profile.bio = request.bio
        if request.country_code is not None:
            profile.country_code = request.country_code
        if request.city is not None:
            profile.city = request.city
        if request.timezone is not None:
            profile.timezone = request.timezone
        if request.hourly_rate_min is not None or request.hourly_rate_max is not None:
            profile.update_rate_range(
                request.hourly_rate_min if request.hourly_rate_min is not None else profile.hourly_rate_min,
                request.hourly_rate_max if request.hourly_rate_max is not None else profile.hourly_rate_max,
            )
        await self._profile_repo.update(profile)
        return to_profile_result(profile)
