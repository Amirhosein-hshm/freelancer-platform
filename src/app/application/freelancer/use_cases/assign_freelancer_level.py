from app.application.freelancer.dto import (
    AssignFreelancerLevelCommand,
    AssignFreelancerLevelResult,
)
from app.application.shared.authorization import IAuthorizationService
from app.application.shared.ports import IClock, IIdGenerator, IUnitOfWork
from app.application.shared.use_case import UseCase
from app.domain.freelancer.entities import FreelancerLevelHistory
from app.domain.freelancer.repositories import (
    IFreelancerLevelHistoryRepository,
    IFreelancerLevelRepository,
    IFreelancerProfileRepository,
)


class AssignFreelancerLevelUseCase(
    UseCase[AssignFreelancerLevelCommand, AssignFreelancerLevelResult]
):
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

    def execute(
        self, request: AssignFreelancerLevelCommand
    ) -> AssignFreelancerLevelResult:
        self._authorization_service.require_permission(
            request.actor_id, "freelancer.assign_level"
        )
        profile = self._profile_repo.get_by_id(request.profile_id)
        level = self._level_repo.get_by_id(request.new_level_id)
        old_level_id = profile.current_level_id
        now = self._clock.now()
        with self._uow:
            profile.change_level(level.id)
            history = FreelancerLevelHistory(
                id=self._id_generator.new_id(),
                freelancer_profile_id=profile.id,
                old_level_id=old_level_id,
                new_level_id=level.id,
                assigned_by_user_id=request.actor_id,
                reason=request.reason,
                assigned_at=now,
                created_at=now,
            )
            self._level_history_repo.add(history)
            self._profile_repo.update(profile)
            self._uow.commit()
        return AssignFreelancerLevelResult(
            profile_id=profile.id,
            old_level_id=old_level_id,
            new_level_id=level.id,
        )
