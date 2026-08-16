from app.application.project.mapping import to_project_result
from app.application.review.dto import GetSupervisorProjectsQuery, GetSupervisorProjectsResult
from app.application.shared.use_case import UseCase
from app.domain.project.repositories import IProjectRepository


class GetSupervisorProjectsUseCase(UseCase[GetSupervisorProjectsQuery, GetSupervisorProjectsResult]):
    def __init__(self, project_repo: IProjectRepository) -> None:
        self._project_repo = project_repo

    async def execute(self, request: GetSupervisorProjectsQuery) -> GetSupervisorProjectsResult:
        projects = await self._project_repo.list_by_supervisor(request.supervisor_user_id)
        return GetSupervisorProjectsResult(projects=[to_project_result(p) for p in projects])
