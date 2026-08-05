from app.application.project.dto import (
    AdminApplyForProjectOnBehalfCommand,
    ApplyForProjectResult,
)
from app.application.project.permissions import PERMISSION_PROJECT_APPLY_ON_BEHALF
from app.application.project.use_cases.apply_for_project import _apply_for_project
from app.application.shared.authorization import IAuthorizationService
from app.application.shared.ports import IClock, IIdGenerator, IUnitOfWork
from app.application.shared.use_case import UseCase
from app.domain.freelancer.repositories import (
    IFreelancerLevelRepository,
    IFreelancerProfileRepository,
)
from app.domain.project.repositories import (
    IProjectApplicationRepository,
    IProjectRepository,
)


class AdminApplyForProjectOnBehalfUseCase(
    UseCase[AdminApplyForProjectOnBehalfCommand, ApplyForProjectResult]
):
    """Pattern B: an admin submits an application for a specific freelancer profile.

    The permission key ``project.apply_on_behalf`` is admin-only; the real performer is
    recorded in ``ProjectApplication.submitted_by_user_id`` (the admin), while the
    application belongs to the target profile's owner.
    """

    def __init__(
        self,
        authorization_service: IAuthorizationService,
        project_repo: IProjectRepository,
        application_repo: IProjectApplicationRepository,
        profile_repo: IFreelancerProfileRepository,
        level_repo: IFreelancerLevelRepository,
        id_generator: IIdGenerator,
        clock: IClock,
        uow: IUnitOfWork,
    ) -> None:
        self._authorization_service = authorization_service
        self._project_repo = project_repo
        self._application_repo = application_repo
        self._profile_repo = profile_repo
        self._level_repo = level_repo
        self._id_generator = id_generator
        self._clock = clock
        self._uow = uow

    async def execute(
        self, request: AdminApplyForProjectOnBehalfCommand
    ) -> ApplyForProjectResult:
        await self._authorization_service.require_permission(
            request.actor_id, PERMISSION_PROJECT_APPLY_ON_BEHALF
        )
        await self._profile_repo.get_by_id(request.target_freelancer_profile_id)
        return await _apply_for_project(
            freelancer_profile_id=request.target_freelancer_profile_id,
            submitted_by_user_id=request.actor_id,
            project_id=request.project_id,
            cover_letter=request.cover_letter,
            proposed_amount=request.proposed_amount,
            proposed_days=request.proposed_days,
            project_repo=self._project_repo,
            application_repo=self._application_repo,
            profile_repo=self._profile_repo,
            level_repo=self._level_repo,
            id_generator=self._id_generator,
            clock=self._clock,
            uow=self._uow,
        )
