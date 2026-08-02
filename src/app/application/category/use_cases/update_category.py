from app.application.category.dto import CategoryResult, UpdateCategoryCommand
from app.application.category.use_cases.create_category import _to_result
from app.application.shared.ports import IUnitOfWork
from app.application.shared.use_case import UseCase
from app.domain.category.exceptions import CategoryNotFoundError, DuplicateCategorySlugError
from app.domain.category.repositories import ICategoryRepository


class UpdateCategoryUseCase(UseCase[UpdateCategoryCommand, CategoryResult]):
    def __init__(self, category_repo: ICategoryRepository, uow: IUnitOfWork) -> None:
        self._category_repo = category_repo
        self._uow = uow

    def execute(self, request: UpdateCategoryCommand) -> CategoryResult:
        request.validate()
        category = self._category_repo.get_by_id(request.category_id)
        if category.slug != request.slug:
            try:
                existing = self._category_repo.get_by_slug(request.slug)
            except CategoryNotFoundError:
                pass
            else:
                if existing.id != category.id:
                    raise DuplicateCategorySlugError(
                        f"Category slug '{request.slug}' already exists."
                    )
        with self._uow:
            category.rename(request.name, request.slug)
            category.description = request.description
            category.sort_order = request.sort_order
            self._category_repo.update(category)
            self._uow.commit()
        return _to_result(category)
