from app.application.project.dto import (
    ViewApplicationsQuery,
    ViewApplicationsResult,
)
from app.application.project.mapping import to_application_result
from app.application.project.permissions import (
    PERMISSION_PROJECT_MANAGE_ANY,
    PERMISSION_PROJECT_MANAGE_OWN,
)
from app.application.shared.authorization import (
    IAuthorizationService,
    authorize_owned_action,
)
from app.application.shared.pagination import limit_offset
from app.application.shared.use_case import UseCase
from app.domain.project.repositories import (
    IProjectApplicationRepository,
    IProjectRepository,
)


class ViewApplicationsUseCase(UseCase[ViewApplicationsQuery, ViewApplicationsResult]):
    def __init__(
        self,
        authorization_service: IAuthorizationService,
        project_repo: IProjectRepository,
        application_repo: IProjectApplicationRepository,
    ) -> None:
        self._authorization_service = authorization_service
        self._project_repo = project_repo
        self._application_repo = application_repo

    async def execute(self, request: ViewApplicationsQuery) -> ViewApplicationsResult:
        project = await self._project_repo.get_by_id(request.project_id)
        await authorize_owned_action(
            self._authorization_service,
            request.actor_id,
            project.customer_user_id,
            PERMISSION_PROJECT_MANAGE_OWN,
            PERMISSION_PROJECT_MANAGE_ANY,
        )
        limit, offset = limit_offset(request.page, request.page_size)
        applications = await self._application_repo.list_by_project(
            project.id,
            limit=limit,
            offset=offset,
        )
        total_items = await self._application_repo.count_by_project(project.id)
        return ViewApplicationsResult(
            project_id=project.id,
            applications=[to_application_result(a) for a in applications],
            total_items=total_items,
            page=request.page,
            page_size=request.page_size,
        )