from app.application.project.dto import ListVisibleProjectsQuery, ListVisibleProjectsResult
from app.application.project.mapping import to_project_result
from app.application.project.permissions import PERMISSION_PROJECT_MANAGE_ANY
from app.application.shared.authorization import IAuthorizationService
from app.application.shared.exceptions import PermissionDeniedError
from app.application.shared.pagination import limit_offset
from app.application.shared.use_case import UseCase
from app.domain.category.repositories import ICategorySupervisorRepository
from app.domain.project.repositories import IProjectRepository


class ListVisibleProjectsUseCase(UseCase[ListVisibleProjectsQuery, ListVisibleProjectsResult]):
    def __init__(
        self,
        project_repo: IProjectRepository,
        authorization_service: IAuthorizationService,
        category_supervisor_repo: ICategorySupervisorRepository,
    ) -> None:
        self._project_repo = project_repo
        self._authorization_service = authorization_service
        self._category_supervisor_repo = category_supervisor_repo

    async def execute(self, request: ListVisibleProjectsQuery) -> ListVisibleProjectsResult:
        limit, offset = limit_offset(request.page, request.page_size)

        if await self._authorization_service.has_permission(request.actor_id, PERMISSION_PROJECT_MANAGE_ANY):
            projects = await self._project_repo.list_all(limit=limit, offset=offset)
            total_items = await self._project_repo.count_all()
        else:
            recognized = any(
                [
                    await self._authorization_service.has_role(request.actor_id, "customer"),
                    await self._authorization_service.has_role(request.actor_id, "supervisor"),
                    await self._authorization_service.has_role(request.actor_id, "freelancer"),
                ]
            )
            if not recognized:
                raise PermissionDeniedError(f"User {request.actor_id} cannot list projects.")
            if await self._authorization_service.has_role(request.actor_id, "supervisor"):
                projects = await self._project_repo.list_by_supervisor(request.actor_id, limit, offset)
                total_items = await self._project_repo.count_by_supervisor(request.actor_id)
            else:
                projects = await self._project_repo.list_related_to_user(request.actor_id, limit=limit, offset=offset)
                total_items = await self._project_repo.count_related_to_user(request.actor_id)

        return ListVisibleProjectsResult(
            projects=[to_project_result(project) for project in projects],
            total_items=total_items,
            page=request.page,
            page_size=request.page_size,
        )
