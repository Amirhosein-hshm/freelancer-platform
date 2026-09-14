from app.application.project.dto import (
    GetProjectRevisionRequestQuery,
    ProjectRevisionRequestResult,
)
from app.application.project.permissions import (
    PERMISSION_PROJECT_MANAGE_ANY,
    PERMISSION_PROJECT_MANAGE_OWN,
)
from app.application.shared.authorization import IAuthorizationService
from app.application.shared.exceptions import PermissionDeniedError
from app.application.shared.use_case import UseCase
from app.domain.freelancer.repositories import IFreelancerProfileRepository
from app.domain.project.repositories import (
    IProjectApplicationRepository,
    IProjectRepository,
    IProjectRevisionRequestRepository,
)


class GetProjectRevisionRequestUseCase(UseCase[GetProjectRevisionRequestQuery, ProjectRevisionRequestResult]):
    def __init__(
        self,
        authorization_service: IAuthorizationService,
        project_repo: IProjectRepository,
        revision_repo: IProjectRevisionRequestRepository,
        application_repo: IProjectApplicationRepository,
        profile_repo: IFreelancerProfileRepository,
    ) -> None:
        self._authorization_service = authorization_service
        self._project_repo = project_repo
        self._revision_repo = revision_repo
        self._application_repo = application_repo
        self._profile_repo = profile_repo

    async def execute(self, request: GetProjectRevisionRequestQuery) -> ProjectRevisionRequestResult:
        revision = await self._revision_repo.get_by_id(request.revision_id)
        project = await self._project_repo.get_by_id(revision.project_id)
        if await self._authorization_service.has_permission(request.actor_id, PERMISSION_PROJECT_MANAGE_ANY):
            pass
        elif request.actor_id == project.customer_user_id:
            await self._authorization_service.require_permission(request.actor_id, PERMISSION_PROJECT_MANAGE_OWN)
        elif project.selected_application_id is not None:
            application = await self._application_repo.get_by_id(project.selected_application_id)
            profile = await self._profile_repo.get_by_id(application.freelancer_profile_id)
            if profile.user_id != request.actor_id:
                raise PermissionDeniedError("User cannot access project revision.")
        else:
            raise PermissionDeniedError("User cannot access project revision.")
        return ProjectRevisionRequestResult(
            revision_id=revision.id,
            project_id=revision.project_id,
            project_delivery_id=revision.project_delivery_id,
            requested_by_user_id=revision.requested_by_user_id,
            requested_to_user_id=revision.requested_to_user_id,
            round_no=revision.round_no,
            status=revision.status.value,
            reason=revision.reason,
            resolved_by_user_id=revision.resolved_by_user_id,
            requested_at=revision.requested_at,
            resolved_at=revision.resolved_at,
        )
