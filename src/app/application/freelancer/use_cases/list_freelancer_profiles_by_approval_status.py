from app.application.freelancer.dto import (
    FreelancerProfileResult,
    ListFreelancerProfilesByApprovalStatusQuery,
    ListFreelancerProfilesByApprovalStatusResult,
)
from app.application.freelancer.permissions import PERMISSION_FREELANCER_READ_ANY
from app.application.shared.authorization import IAuthorizationService
from app.application.shared.pagination import limit_offset
from app.application.shared.use_case import UseCase
from app.domain.freelancer.repositories import IFreelancerProfileRepository


class ListFreelancerProfilesByApprovalStatusUseCase(
    UseCase[ListFreelancerProfilesByApprovalStatusQuery, ListFreelancerProfilesByApprovalStatusResult]
):
    def __init__(
        self,
        authorization_service: IAuthorizationService,
        profile_repo: IFreelancerProfileRepository,
    ) -> None:
        self._authorization_service = authorization_service
        self._profile_repo = profile_repo

    async def execute(
        self, request: ListFreelancerProfilesByApprovalStatusQuery
    ) -> ListFreelancerProfilesByApprovalStatusResult:
        await self._authorization_service.require_permission(request.actor_id, PERMISSION_FREELANCER_READ_ANY)
        limit, offset = limit_offset(request.page, request.page_size)
        profiles = await self._profile_repo.list_by_approval_status(
            request.status,
            limit=limit,
            offset=offset,
        )
        total_items = await self._profile_repo.count_by_approval_status(request.status)
        return ListFreelancerProfilesByApprovalStatusResult(
            profiles=[
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
                    current_level=p.current_level,
                    approval_status=p.approval_status,
                    approved_at=p.approved_at,
                )
                for p in profiles
            ],
            total_items=total_items,
            page=request.page,
            page_size=request.page_size,
        )