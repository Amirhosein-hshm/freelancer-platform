from app.application.category.dto import CategoryResult, UpdateCategoryCommand
from app.application.category.use_cases.create_category import (
    PERMISSION_CATEGORY_MANAGE,
    _to_result,
)
from app.application.shared.authorization import IAuthorizationService
from app.application.shared.ports import IUnitOfWork
from app.application.shared.use_case import UseCase
from app.domain.category.exceptions import CategoryNotFoundError, DuplicateCategorySlugError
from app.domain.category.repositories import ICategoryRepository


class UpdateCategoryUseCase(UseCase[UpdateCategoryCommand, CategoryResult]):
    def __init__(
        self,
        authorization_service: IAuthorizationService,
        category_repo: ICategoryRepository,
        uow: IUnitOfWork,
    ) -> None:
        self._authorization_service = authorization_service
        self._category_repo = category_repo
        self._uow = uow

    async def execute(self, request: UpdateCategoryCommand) -> CategoryResult:
        await self._authorization_service.require_permission(request.actor_id, PERMISSION_CATEGORY_MANAGE)
        request.validate()
        category = await self._category_repo.get_by_id(request.category_id)
        if category.slug != request.slug:
            try:
                existing = await self._category_repo.get_by_slug(request.slug)
            except CategoryNotFoundError:
                pass
            else:
                if existing.id != category.id:
                    raise DuplicateCategorySlugError(f"Category slug '{request.slug}' already exists.")
        async with self._uow:
            category.rename(request.name, request.slug)
            category.description = request.description
            category.sort_order = request.sort_order
            await self._category_repo.update(category)
            await self._uow.commit()
        return _to_result(category)
