from decimal import Decimal

from app.application.project.dto import (
    ApplyForProjectCommand,
    ApplyForProjectResult,
)
from app.application.project.permissions import PERMISSION_PROJECT_APPLY
from app.application.shared.authorization import IAuthorizationService
from app.application.shared.ports import IClock, IIdGenerator, IUnitOfWork
from app.application.shared.use_case import UseCase
from app.domain.freelancer.exceptions import FreelancerNotApprovedError
from app.domain.freelancer.repositories import IFreelancerProfileRepository
from app.domain.project.entities import ProjectApplication
from app.domain.project.enums import ProjectApplicationStatus
from app.domain.project.exceptions import (
    ApplicationDeadlineExpiredError,
    DuplicateApplicationError,
    FreelancerNotEligibleError,
)
from app.domain.project.repositories import (
    IProjectApplicationRepository,
    IProjectRepository,
)
from app.domain.project.services import FreelancerEligibilityPolicy
from app.domain.shared.types import EntityId


async def _apply_for_project(
    *,
    freelancer_profile_id: EntityId,
    submitted_by_user_id: EntityId,
    project_id: EntityId,
    cover_letter: str | None,
    proposed_amount: Decimal | None,
    proposed_days: int | None,
    project_repo: IProjectRepository,
    application_repo: IProjectApplicationRepository,
    profile_repo: IFreelancerProfileRepository,
    id_generator: IIdGenerator,
    clock: IClock,
    uow: IUnitOfWork,
) -> ApplyForProjectResult:
    project = await project_repo.get_by_id(project_id)
    if not project.can_accept_applications():
        raise FreelancerNotEligibleError(
            f"Project {project_id} is not accepting applications (status '{project.status.value}')."
        )
    now = await clock.now()
    if project.is_application_deadline_passed(now):
        raise ApplicationDeadlineExpiredError(f"Project {project_id} application deadline has passed.")
    profile = await profile_repo.get_by_id(freelancer_profile_id)
    if not profile.is_approved():
        raise FreelancerNotApprovedError(f"Freelancer profile {profile.id} is not approved.")
    existing = await application_repo.find_by_project_and_freelancer(project.id, profile.id)
    if existing is not None:
        raise DuplicateApplicationError(f"Freelancer {profile.id} already applied to project {project.id}.")
    active_count = await application_repo.count_active_for_freelancer(profile.id)
    if not FreelancerEligibilityPolicy.is_eligible_to_apply(profile.current_level, project, active_count):
        raise FreelancerNotEligibleError(
            f"Freelancer {profile.id} is not eligible to apply to project {project.id} "
            f"at level '{(profile.current_level.value if profile.current_level else 'unassigned')}'."
        )
    application = ProjectApplication(
        id=await id_generator.new_id(),
        project_id=project.id,
        freelancer_profile_id=profile.id,
        status=ProjectApplicationStatus.APPLIED,
        cover_letter=cover_letter,
        proposed_amount=proposed_amount,
        proposed_days=proposed_days,
        applied_at=now,
        submitted_by_user_id=submitted_by_user_id,
        decided_by_user_id=None,
        decided_at=None,
        decision_note=None,
        withdrawn_at=None,
        created_at=now,
    )
    async with uow:
        await application_repo.add(application)
        await uow.commit()
    return ApplyForProjectResult(
        application_id=application.id,
        status=application.status,
    )


class ApplyForProjectUseCase(UseCase[ApplyForProjectCommand, ApplyForProjectResult]):
    def __init__(
        self,
        authorization_service: IAuthorizationService,
        project_repo: IProjectRepository,
        application_repo: IProjectApplicationRepository,
        profile_repo: IFreelancerProfileRepository,
        id_generator: IIdGenerator,
        clock: IClock,
        uow: IUnitOfWork,
    ) -> None:
        self._authorization_service = authorization_service
        self._project_repo = project_repo
        self._application_repo = application_repo
        self._profile_repo = profile_repo
        self._id_generator = id_generator
        self._clock = clock
        self._uow = uow

    async def execute(self, request: ApplyForProjectCommand) -> ApplyForProjectResult:
        await self._authorization_service.require_permission(request.actor_id, PERMISSION_PROJECT_APPLY)
        profile = await self._profile_repo.get_by_user_id(request.actor_id)
        return await _apply_for_project(
            freelancer_profile_id=profile.id,
            submitted_by_user_id=request.actor_id,
            project_id=request.project_id,
            cover_letter=request.cover_letter,
            proposed_amount=request.proposed_amount,
            proposed_days=request.proposed_days,
            project_repo=self._project_repo,
            application_repo=self._application_repo,
            profile_repo=self._profile_repo,
            id_generator=self._id_generator,
            clock=self._clock,
            uow=self._uow,
        )
