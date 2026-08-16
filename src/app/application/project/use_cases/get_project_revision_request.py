from app.application.project.dto import (
    GetProjectRevisionRequestQuery,
    ProjectRevisionRequestResult,
)
from app.application.project.permissions import (
    PERMISSION_PROJECT_MANAGE_ANY,
    PERMISSION_PROJECT_MANAGE_OWN,
)
from app.application.shared.authorization import IAuthorizationService, authorize_owned_action
from app.application.shared.use_case import UseCase
from app.domain.project.repositories import (
    IProjectRepository,
    IProjectRevisionRequestRepository,
)


class GetProjectRevisionRequestUseCase(UseCase[GetProjectRevisionRequestQuery, ProjectRevisionRequestResult]):
    def __init__(
        self,
        authorization_service: IAuthorizationService,
        project_repo: IProjectRepository,
        revision_repo: IProjectRevisionRequestRepository,
    ) -> None:
        self._authorization_service = authorization_service
        self._project_repo = project_repo
        self._revision_repo = revision_repo

    async def execute(self, request: GetProjectRevisionRequestQuery) -> ProjectRevisionRequestResult:
        revision = await self._revision_repo.get_by_id(request.revision_id)
        project = await self._project_repo.get_by_id(revision.project_id)
        await authorize_owned_action(
            self._authorization_service,
            request.actor_id,
            project.customer_user_id,
            PERMISSION_PROJECT_MANAGE_OWN,
            PERMISSION_PROJECT_MANAGE_ANY,
        )
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
