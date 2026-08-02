from app.application.project.dto import (
    ViewApplicationsQuery,
    ViewApplicationsResult,
)
from app.application.project.mapping import to_application_result
from app.application.shared.exceptions import PermissionDeniedError
from app.application.shared.use_case import UseCase
from app.domain.project.repositories import (
    IProjectApplicationRepository,
    IProjectRepository,
)


class ViewApplicationsUseCase(UseCase[ViewApplicationsQuery, ViewApplicationsResult]):
    def __init__(
        self,
        project_repo: IProjectRepository,
        application_repo: IProjectApplicationRepository,
    ) -> None:
        self._project_repo = project_repo
        self._application_repo = application_repo

    def execute(self, request: ViewApplicationsQuery) -> ViewApplicationsResult:
        project = self._project_repo.get_by_id(request.project_id)
        if project.customer_user_id != request.actor_id:
            raise PermissionDeniedError(
                f"User {request.actor_id} cannot view applications of project "
                f"{request.project_id}."
            )
        applications = self._application_repo.list_by_project(project.id)
        return ViewApplicationsResult(
            project_id=project.id,
            applications=[to_application_result(a) for a in applications],
        )
