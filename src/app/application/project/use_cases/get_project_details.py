from app.application.project.dto import (
    GetProjectDetailsQuery,
    GetProjectDetailsResult,
)
from app.application.project.mapping import (
    to_application_result,
    to_delivery_result,
    to_project_result,
)
from app.application.shared.use_case import UseCase
from app.domain.project.repositories import (
    IProjectApplicationRepository,
    IProjectDeliveryRepository,
    IProjectRepository,
)


class GetProjectDetailsUseCase(UseCase[GetProjectDetailsQuery, GetProjectDetailsResult]):
    def __init__(
        self,
        project_repo: IProjectRepository,
        application_repo: IProjectApplicationRepository,
        delivery_repo: IProjectDeliveryRepository,
    ) -> None:
        self._project_repo = project_repo
        self._application_repo = application_repo
        self._delivery_repo = delivery_repo

    def execute(self, request: GetProjectDetailsQuery) -> GetProjectDetailsResult:
        project = self._project_repo.get_by_id(request.project_id)
        applications = self._application_repo.list_by_project(project.id)
        deliveries = self._delivery_repo.list_by_project(project.id)
        return GetProjectDetailsResult(
            project=to_project_result(project),
            applications=[to_application_result(a) for a in applications],
            deliveries=[to_delivery_result(d) for d in deliveries],
        )
