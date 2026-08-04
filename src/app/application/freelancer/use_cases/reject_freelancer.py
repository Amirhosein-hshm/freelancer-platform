from app.application.freelancer.dto import (
    RejectFreelancerCommand,
    RejectFreelancerResult,
)
from app.application.shared.authorization import IAuthorizationService
from app.application.shared.ports import IClock, IUnitOfWork
from app.application.shared.use_case import UseCase
from app.domain.freelancer.repositories import IFreelancerProfileRepository


class RejectFreelancerUseCase(UseCase[RejectFreelancerCommand, RejectFreelancerResult]):
    def __init__(
        self,
        authorization_service: IAuthorizationService,
        profile_repo: IFreelancerProfileRepository,
        clock: IClock,
        uow: IUnitOfWork,
    ) -> None:
        self._authorization_service = authorization_service
        self._profile_repo = profile_repo
        self._clock = clock
        self._uow = uow

    async def execute(self, request: RejectFreelancerCommand) -> RejectFreelancerResult:
        await self._authorization_service.require_permission(request.actor_id, "freelancer.approve")
        profile = await self._profile_repo.get_by_id(request.profile_id)
        now = await self._clock.now()
        async with self._uow:
            profile.reject(request.actor_id, now, request.note)
            await self._profile_repo.update(profile)
            await self._uow.commit()
        return RejectFreelancerResult(
            profile_id=profile.id,
            approval_status=profile.approval_status,
        )
