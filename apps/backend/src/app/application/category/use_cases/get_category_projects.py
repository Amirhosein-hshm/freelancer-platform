from dataclasses import dataclass

from app.application.project.dto import ProjectResult
from app.application.project.mapping import to_project_result
from app.application.shared.pagination import DEFAULT_PAGE_SIZE, limit_offset
from app.application.shared.use_case import UseCase
from app.domain.category.repositories import ICategoryRepository
from app.domain.project.repositories import IProjectRepository
from app.domain.shared.types import EntityId


@dataclass(frozen=True)
class GetCategoryProjectsQuery:
    category_id: EntityId
    page: int = 1
    page_size: int = DEFAULT_PAGE_SIZE


@dataclass(frozen=True)
class GetCategoryProjectsResult:
    category_id: EntityId
    projects: list[ProjectResult]
    total_items: int
    page: int
    page_size: int


class GetCategoryProjectsUseCase(UseCase[GetCategoryProjectsQuery, GetCategoryProjectsResult]):
    def __init__(
        self,
        category_repo: ICategoryRepository,
        project_repo: IProjectRepository,
    ) -> None:
        self._category_repo = category_repo
        self._project_repo = project_repo

    async def execute(self, request: GetCategoryProjectsQuery) -> GetCategoryProjectsResult:
        await self._category_repo.get_by_id(request.category_id)
        limit, offset = limit_offset(request.page, request.page_size)
        projects = await self._project_repo.list_by_category(
            request.category_id,
            limit=limit,
            offset=offset,
        )
        total_items = await self._project_repo.count_open_by_category(request.category_id)
        return GetCategoryProjectsResult(
            category_id=request.category_id,
            projects=[to_project_result(p) for p in projects],
            total_items=total_items,
            page=request.page,
            page_size=request.page_size,
        )