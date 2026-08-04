from app.application.category.dto import GetCategoriesQuery, GetCategoriesResult
from app.application.category.use_cases.create_category import _to_result
from app.application.shared.use_case import UseCase
from app.domain.category.repositories import ICategoryRepository


class GetCategoriesUseCase(UseCase[GetCategoriesQuery, GetCategoriesResult]):
    def __init__(self, category_repo: ICategoryRepository) -> None:
        self._category_repo = category_repo

    async def execute(self, request: GetCategoriesQuery) -> GetCategoriesResult:
        categories = await self._category_repo.list_active()
        return GetCategoriesResult(categories=[_to_result(c) for c in categories])
