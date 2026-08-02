from app.application.project.dto import (
    ApplyForProjectCommand,
    ApplyForProjectResult,
)
from app.application.shared.ports import IClock, IIdGenerator, IUnitOfWork
from app.application.shared.use_case import UseCase
from app.domain.freelancer.exceptions import FreelancerNotApprovedError
from app.domain.freelancer.repositories import (
    IFreelancerLevelRepository,
    IFreelancerProfileRepository,
)
from app.domain.project.entities import ProjectApplication
from app.domain.project.enums import ProjectApplicationStatus
from app.domain.project.exceptions import (
    DuplicateApplicationError,
    FreelancerNotEligibleError,
)
from app.domain.project.repositories import (
    IProjectApplicationRepository,
    IProjectRepository,
)
from app.domain.project.services import FreelancerEligibilityPolicy


class ApplyForProjectUseCase(UseCase[ApplyForProjectCommand, ApplyForProjectResult]):
    def __init__(
        self,
        project_repo: IProjectRepository,
        application_repo: IProjectApplicationRepository,
        profile_repo: IFreelancerProfileRepository,
        level_repo: IFreelancerLevelRepository,
        id_generator: IIdGenerator,
        clock: IClock,
        uow: IUnitOfWork,
    ) -> None:
        self._project_repo = project_repo
        self._application_repo = application_repo
        self._profile_repo = profile_repo
        self._level_repo = level_repo
        self._id_generator = id_generator
        self._clock = clock
        self._uow = uow

    def execute(self, request: ApplyForProjectCommand) -> ApplyForProjectResult:
        project = self._project_repo.get_by_id(request.project_id)
        if not project.can_accept_applications():
            raise FreelancerNotEligibleError(
                f"Project {request.project_id} is not accepting applications "
                f"(status '{project.status.value}')."
            )
        profile = self._profile_repo.get_by_user_id(request.actor_id)
        if not profile.is_approved():
            raise FreelancerNotApprovedError(
                f"Freelancer profile {profile.id} is not approved."
            )
        existing = self._application_repo.find_by_project_and_freelancer(
            project.id, profile.id
        )
        if existing is not None:
            raise DuplicateApplicationError(
                f"Freelancer {profile.id} already applied to project {project.id}."
            )
        if profile.current_level_id is None:
            raise FreelancerNotEligibleError(
                f"Freelancer {profile.id} has no assigned level and cannot apply."
            )
        level = self._level_repo.get_by_id(profile.current_level_id)
        active_count = self._application_repo.count_active_for_freelancer(profile.id)
        if not FreelancerEligibilityPolicy.is_eligible_to_apply(
            level, project, active_count
        ):
            raise FreelancerNotEligibleError(
                f"Freelancer {profile.id} is not eligible to apply to project {project.id} "
                "at level '{level.level_key}'."
            )
        now = self._clock.now()
        application = ProjectApplication(
            id=self._id_generator.new_id(),
            project_id=project.id,
            freelancer_profile_id=profile.id,
            status=ProjectApplicationStatus.APPLIED,
            cover_letter=request.cover_letter,
            proposed_amount=request.proposed_amount,
            proposed_days=request.proposed_days,
            applied_at=now,
            decided_by_user_id=None,
            decided_at=None,
            decision_note=None,
            withdrawn_at=None,
            created_at=now,
        )
        with self._uow:
            self._application_repo.add(application)
            self._uow.commit()
        return ApplyForProjectResult(
            application_id=application.id,
            status=application.status,
        )
