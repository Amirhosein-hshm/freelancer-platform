from app.application.project.dto import (
    ListProjectStatusHistoryQuery,
    ListProjectStatusHistoryResult,
    ProjectStatusHistoryResult,
)
from app.application.project.permissions import (
    PERMISSION_PROJECT_MANAGE_ANY,
    PERMISSION_PROJECT_MANAGE_OWN,
)
from app.application.shared.authorization import IAuthorizationService, authorize_owned_action
from app.application.shared.pagination import limit_offset
from app.application.shared.use_case import UseCase
from app.domain.project.repositories import (
    IProjectRepository,
    IProjectStatusHistoryRepository,
)


class ListProjectStatusHistoryUseCase(UseCase[ListProjectStatusHistoryQuery, ListProjectStatusHistoryResult]):
    def __init__(
        self,
        authorization_service: IAuthorizationService,
        project_repo: IProjectRepository,
        status_history_repo: IProjectStatusHistoryRepository,
    ) -> None:
        self._authorization_service = authorization_service
        self._project_repo = project_repo
        self._status_history_repo = status_history_repo

    async def execute(self, request: ListProjectStatusHistoryQuery) -> ListProjectStatusHistoryResult:
        project = await self._project_repo.get_by_id(request.project_id)
        await authorize_owned_action(
            self._authorization_service,
            request.actor_id,
            project.customer_user_id,
            PERMISSION_PROJECT_MANAGE_OWN,
            PERMISSION_PROJECT_MANAGE_ANY,
        )
        limit, offset = limit_offset(request.page, request.page_size)
        history = await self._status_history_repo.list_by_project(
            request.project_id,
            limit=limit,
            offset=offset,
        )
        total_items = await self._status_history_repo.count_by_project(request.project_id)
        return ListProjectStatusHistoryResult(
            history=[
                ProjectStatusHistoryResult(
                    history_id=h.id,
                    project_id=h.project_id,
                    from_status=h.from_status.value if h.from_status else None,
                    to_status=h.to_status.value,
                    changed_by_user_id=h.changed_by_user_id,
                    reason=h.reason,
                    changed_at=h.changed_at,
                )
                for h in history
            ],
            total_items=total_items,
            page=request.page,
            page_size=request.page_size,
        )