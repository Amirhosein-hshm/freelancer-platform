from app.application.project.dto import (
    WithdrawApplicationCommand,
    WithdrawApplicationResult,
)
from app.application.shared.exceptions import PermissionDeniedError
from app.application.shared.ports import IClock, IUnitOfWork
from app.application.shared.use_case import UseCase
from app.domain.freelancer.repositories import IFreelancerProfileRepository
from app.domain.project.repositories import (
    IProjectApplicationRepository,
)


class WithdrawApplicationUseCase(
    UseCase[WithdrawApplicationCommand, WithdrawApplicationResult]
):
    def __init__(
        self,
        application_repo: IProjectApplicationRepository,
        profile_repo: IFreelancerProfileRepository,
        clock: IClock,
        uow: IUnitOfWork,
    ) -> None:
        self._application_repo = application_repo
        self._profile_repo = profile_repo
        self._clock = clock
        self._uow = uow

    async def execute(self, request: WithdrawApplicationCommand) -> WithdrawApplicationResult:
        application = await self._application_repo.get_by_id(request.application_id)
        profile = await self._profile_repo.get_by_user_id(request.actor_id)
        if application.freelancer_profile_id != profile.id:
            raise PermissionDeniedError(
                f"User {request.actor_id} does not own application {request.application_id}."
            )
        now = await self._clock.now()
        async with self._uow:
            application.withdraw(now)
            await self._application_repo.update(application)
            await self._uow.commit()
        return WithdrawApplicationResult(
            application_id=application.id,
            status=application.status,
        )
