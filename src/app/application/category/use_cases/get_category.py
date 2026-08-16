from app.application.category.dto import GetCategoryQuery, GetCategoryResult
from app.application.shared.use_case import UseCase
from app.domain.category.repositories import ICategoryRepository


class GetCategoryUseCase(UseCase[GetCategoryQuery, GetCategoryResult]):
    def __init__(self, category_repo: ICategoryRepository) -> None:
        self._category_repo = category_repo

    async def execute(self, request: GetCategoryQuery) -> GetCategoryResult:
        category = await self._category_repo.get_by_id(request.category_id)
        return GetCategoryResult(
            category_id=category.id,
            category_key=category.category_key,
            name=category.name,
            slug=category.slug,
            description=category.description,
            is_active=category.is_active,
            sort_order=category.sort_order,
            parent_category_id=category.parent_category_id,
        )
