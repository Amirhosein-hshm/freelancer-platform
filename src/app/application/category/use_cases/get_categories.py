from app.application.category.dto import GetCategoriesQuery, GetCategoriesResult
from app.application.category.use_cases.create_category import _to_result
from app.application.shared.pagination import limit_offset
from app.application.shared.use_case import UseCase
from app.domain.category.repositories import ICategoryRepository


class GetCategoriesUseCase(UseCase[GetCategoriesQuery, GetCategoriesResult]):
    def __init__(self, category_repo: ICategoryRepository) -> None:
        self._category_repo = category_repo

    async def execute(self, request: GetCategoriesQuery) -> GetCategoriesResult:
        limit, offset = limit_offset(request.page, request.page_size)
        categories = await self._category_repo.list_active(
            limit=limit,
            offset=offset,
        )
        total_items = await self._category_repo.count_active()
        return GetCategoriesResult(
            categories=[_to_result(c) for c in categories],
            total_items=total_items,
            page=request.page,
            page_size=request.page_size,
        )