from app.application.freelancer.dto import (
    FreelancerProfileResult,
    ListFreelancerProfilesByApprovalStatusQuery,
)
from app.application.freelancer.permissions import PERMISSION_FREELANCER_READ_ANY
from app.application.shared.authorization import IAuthorizationService
from app.application.shared.use_case import UseCase
from app.domain.freelancer.repositories import IFreelancerProfileRepository


class ListFreelancerProfilesByApprovalStatusUseCase(
    UseCase[ListFreelancerProfilesByApprovalStatusQuery, list[FreelancerProfileResult]]
):
    def __init__(
        self,
        authorization_service: IAuthorizationService,
        profile_repo: IFreelancerProfileRepository,
    ) -> None:
        self._authorization_service = authorization_service
        self._profile_repo = profile_repo

    async def execute(self, request: ListFreelancerProfilesByApprovalStatusQuery) -> list[FreelancerProfileResult]:
        await self._authorization_service.require_permission(request.actor_id, PERMISSION_FREELANCER_READ_ANY)
        profiles = await self._profile_repo.list_by_approval_status(request.status)
        return [
            FreelancerProfileResult(
                profile_id=p.id,
                user_id=p.user_id,
                display_name=p.display_name,
                headline=p.headline,
                bio=p.bio,
                country_code=p.country_code,
                city=p.city,
                timezone=p.timezone,
                hourly_rate_min=p.hourly_rate_min,
                hourly_rate_max=p.hourly_rate_max,
                is_available=p.is_available,
                current_level_id=p.current_level_id,
                approval_status=p.approval_status,
                approved_at=p.approved_at,
            )
            for p in profiles
        ]
