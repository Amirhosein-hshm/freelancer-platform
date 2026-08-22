from app.application.project.dto import (
    ListProjectRevisionRequestsQuery,
    ListProjectRevisionRequestsResult,
    ProjectRevisionRequestResult,
)
from app.application.project.permissions import (
    PERMISSION_PROJECT_MANAGE_ANY,
    PERMISSION_PROJECT_MANAGE_OWN,
)
from app.application.shared.authorization import IAuthorizationService
from app.application.shared.exceptions import PermissionDeniedError
from app.application.shared.pagination import limit_offset
from app.application.shared.use_case import UseCase
from app.domain.freelancer.repositories import IFreelancerProfileRepository
from app.domain.project.repositories import (
    IProjectApplicationRepository,
    IProjectRepository,
    IProjectRevisionRequestRepository,
)


class ListProjectRevisionRequestsUseCase(UseCase[ListProjectRevisionRequestsQuery, ListProjectRevisionRequestsResult]):
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

    async def execute(self, request: ListProjectRevisionRequestsQuery) -> ListProjectRevisionRequestsResult:
        project = await self._project_repo.get_by_id(request.project_id)
        if await self._authorization_service.has_permission(request.actor_id, PERMISSION_PROJECT_MANAGE_ANY):
            pass
        elif request.actor_id == project.customer_user_id:
            await self._authorization_service.require_permission(request.actor_id, PERMISSION_PROJECT_MANAGE_OWN)
        elif project.selected_application_id is not None:
            application = await self._application_repo.get_by_id(project.selected_application_id)
            profile = await self._profile_repo.get_by_id(application.freelancer_profile_id)
            if profile.user_id != request.actor_id:
                raise PermissionDeniedError("User cannot access project revisions.")
        else:
            raise PermissionDeniedError("User cannot access project revisions.")
        limit, offset = limit_offset(request.page, request.page_size)
        revisions = await self._revision_repo.list_by_project(
            request.project_id,
            limit=limit,
            offset=offset,
        )
        total_items = await self._revision_repo.count_by_project(request.project_id)
        return ListProjectRevisionRequestsResult(
            revisions=[
                ProjectRevisionRequestResult(
                    revision_id=r.id,
                    project_id=r.project_id,
                    project_delivery_id=r.project_delivery_id,
                    requested_by_user_id=r.requested_by_user_id,
                    requested_to_user_id=r.requested_to_user_id,
                    round_no=r.round_no,
                    status=r.status.value,
                    reason=r.reason,
                    resolved_by_user_id=r.resolved_by_user_id,
                    requested_at=r.requested_at,
                    resolved_at=r.resolved_at,
                )
                for r in revisions
            ],
            total_items=total_items,
            page=request.page,
            page_size=request.page_size,
        )
