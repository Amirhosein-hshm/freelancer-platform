from dataclasses import dataclass

from app.application.project.dto import ProjectResult
from app.application.project.mapping import to_project_result
from app.application.shared.use_case import UseCase
from app.domain.category.repositories import ICategoryRepository
from app.domain.project.repositories import IProjectRepository
from app.domain.shared.types import EntityId


@dataclass(frozen=True)
class GetCategoryProjectsQuery:
    category_id: EntityId


@dataclass(frozen=True)
class GetCategoryProjectsResult:
    category_id: EntityId
    projects: list[ProjectResult]


class GetCategoryProjectsUseCase(
    UseCase[GetCategoryProjectsQuery, GetCategoryProjectsResult]
):
    def __init__(
        self,
        category_repo: ICategoryRepository,
        project_repo: IProjectRepository,
    ) -> None:
        self._category_repo = category_repo
        self._project_repo = project_repo

    def execute(self, request: GetCategoryProjectsQuery) -> GetCategoryProjectsResult:
        self._category_repo.get_by_id(request.category_id)
        projects = self._project_repo.list_by_category(request.category_id)
        return GetCategoryProjectsResult(
            category_id=request.category_id,
            projects=[to_project_result(p) for p in projects],
        )
