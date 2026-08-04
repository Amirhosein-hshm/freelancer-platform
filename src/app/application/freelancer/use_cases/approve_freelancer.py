from app.application.freelancer.dto import (
    ApproveFreelancerCommand,
    ApproveFreelancerResult,
)
from app.application.shared.authorization import IAuthorizationService
from app.application.shared.ports import IClock, IIdGenerator, IUnitOfWork
from app.application.shared.use_case import UseCase
from app.domain.freelancer.entities import FreelancerLevelHistory
from app.domain.freelancer.exceptions import FreelancerLevelNotFoundError
from app.domain.freelancer.repositories import (
    IFreelancerLevelHistoryRepository,
    IFreelancerLevelRepository,
    IFreelancerProfileRepository,
)

DEFAULT_LEVEL_KEY = "standard"


class ApproveFreelancerUseCase(UseCase[ApproveFreelancerCommand, ApproveFreelancerResult]):
    def __init__(
        self,
        authorization_service: IAuthorizationService,
        profile_repo: IFreelancerProfileRepository,
        level_repo: IFreelancerLevelRepository,
        level_history_repo: IFreelancerLevelHistoryRepository,
        id_generator: IIdGenerator,
        clock: IClock,
        uow: IUnitOfWork,
    ) -> None:
        self._authorization_service = authorization_service
        self._profile_repo = profile_repo
        self._level_repo = level_repo
        self._level_history_repo = level_history_repo
        self._id_generator = id_generator
        self._clock = clock
        self._uow = uow

    async def execute(self, request: ApproveFreelancerCommand) -> ApproveFreelancerResult:
        await self._authorization_service.require_permission(request.actor_id, "freelancer.approve")
        profile = await self._profile_repo.get_by_id(request.profile_id)
        now = await self._clock.now()
        async with self._uow:
            profile.approve(request.actor_id, now, request.note)
            old_level_id = profile.current_level_id
            try:
                default_level = await self._level_repo.get_by_key(DEFAULT_LEVEL_KEY)
            except FreelancerLevelNotFoundError:
                default_level = None
            if default_level is not None and profile.current_level_id != default_level.id:
                profile.change_level(default_level.id)
                history = FreelancerLevelHistory(
                    id=await self._id_generator.new_id(),
                    freelancer_profile_id=profile.id,
                    old_level_id=old_level_id,
                    new_level_id=default_level.id,
                    assigned_by_user_id=request.actor_id,
                    reason="Default level granted on approval.",
                    assigned_at=now,
                    created_at=now,
                )
                await self._level_history_repo.add(history)
            await self._profile_repo.update(profile)
            await self._uow.commit()
        return ApproveFreelancerResult(
            profile_id=profile.id,
            approval_status=profile.approval_status,
            current_level_id=profile.current_level_id,
        )
