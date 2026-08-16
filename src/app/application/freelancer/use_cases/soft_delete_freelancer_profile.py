from app.application.freelancer.dto import (
    SoftDeleteFreelancerProfileCommand,
    SoftDeleteFreelancerProfileResult,
)
from app.application.freelancer.permissions import PERMISSION_FREELANCER_DELETE_ANY
from app.application.shared.authorization import IAuthorizationService
from app.application.shared.ports import IClock
from app.application.shared.use_case import UseCase
from app.domain.freelancer.repositories import IFreelancerProfileRepository


class SoftDeleteFreelancerProfileUseCase(
    UseCase[SoftDeleteFreelancerProfileCommand, SoftDeleteFreelancerProfileResult]
):
    def __init__(
        self,
        authorization_service: IAuthorizationService,
        profile_repo: IFreelancerProfileRepository,
        clock: IClock,
    ) -> None:
        self._authorization_service = authorization_service
        self._profile_repo = profile_repo
        self._clock = clock

    async def execute(self, request: SoftDeleteFreelancerProfileCommand) -> SoftDeleteFreelancerProfileResult:
        await self._authorization_service.require_permission(request.actor_id, PERMISSION_FREELANCER_DELETE_ANY)
        profile = await self._profile_repo.get_by_id(request.profile_id)
        profile.soft_delete(await self._clock.now())
        await self._profile_repo.update(profile)
        return SoftDeleteFreelancerProfileResult(profile_id=profile.id)
