from app.application.project.dto import ApplicationResult, GetProjectApplicationQuery
from app.application.project.permissions import (
    PERMISSION_PROJECT_APPLY,
    PERMISSION_PROJECT_MANAGE_ANY,
    PERMISSION_PROJECT_MANAGE_OWN,
)
from app.application.shared.authorization import IAuthorizationService
from app.application.shared.use_case import UseCase
from app.domain.freelancer.repositories import IFreelancerProfileRepository
from app.domain.project.repositories import IProjectApplicationRepository, IProjectRepository


class GetProjectApplicationUseCase(UseCase[GetProjectApplicationQuery, ApplicationResult]):
    def __init__(
        self,
        authorization_service: IAuthorizationService,
        project_repo: IProjectRepository,
        application_repo: IProjectApplicationRepository,
        profile_repo: IFreelancerProfileRepository,
    ) -> None:
        self._authorization_service = authorization_service
        self._project_repo = project_repo
        self._application_repo = application_repo
        self._profile_repo = profile_repo

    async def execute(self, request: GetProjectApplicationQuery) -> ApplicationResult:
        application = await self._application_repo.get_by_id(request.application_id)
        project = await self._project_repo.get_by_id(application.project_id)
        profile = await self._profile_repo.get_by_id(application.freelancer_profile_id)

        if request.actor_id == profile.user_id:
            await self._authorization_service.require_permission(request.actor_id, PERMISSION_PROJECT_APPLY)
        elif request.actor_id == project.customer_user_id:
            await self._authorization_service.require_permission(request.actor_id, PERMISSION_PROJECT_MANAGE_OWN)
        else:
            await self._authorization_service.require_permission(request.actor_id, PERMISSION_PROJECT_MANAGE_ANY)

        return ApplicationResult(
            application_id=application.id,
            project_id=application.project_id,
            freelancer_profile_id=application.freelancer_profile_id,
            status=application.status,
            cover_letter=application.cover_letter,
            proposed_amount=application.proposed_amount,
            proposed_days=application.proposed_days,
            applied_at=application.applied_at,
            submitted_by_user_id=application.submitted_by_user_id,
            decided_at=application.decided_at,
            decision_note=application.decision_note,
        )
