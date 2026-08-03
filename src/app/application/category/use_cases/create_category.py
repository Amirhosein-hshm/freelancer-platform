from app.application.category.dto import (
    CategoryResult,
    CreateCategoryCommand,
)
from app.application.shared.authorization import IAuthorizationService
from app.application.shared.ports import IClock, IIdGenerator, IUnitOfWork
from app.application.shared.use_case import UseCase
from app.domain.category.entities import Category
from app.domain.category.exceptions import CategoryNotFoundError, DuplicateCategorySlugError
from app.domain.category.repositories import ICategoryRepository

PERMISSION_CATEGORY_MANAGE = "category.manage"


def _to_result(category: Category) -> CategoryResult:
    return CategoryResult(
        category_id=category.id,
        category_key=category.category_key,
        name=category.name,
        slug=category.slug,
        description=category.description,
        is_active=category.is_active,
        sort_order=category.sort_order,
        parent_category_id=category.parent_category_id,
    )


class CreateCategoryUseCase(UseCase[CreateCategoryCommand, CategoryResult]):
    def __init__(
        self,
        authorization_service: IAuthorizationService,
        category_repo: ICategoryRepository,
        id_generator: IIdGenerator,
        clock: IClock,
        uow: IUnitOfWork,
    ) -> None:
        self._authorization_service = authorization_service
        self._category_repo = category_repo
        self._id_generator = id_generator
        self._clock = clock
        self._uow = uow

    def execute(self, request: CreateCategoryCommand) -> CategoryResult:
        self._authorization_service.require_permission(
            request.actor_id, PERMISSION_CATEGORY_MANAGE
        )
        request.validate()
        try:
            self._category_repo.get_by_slug(request.slug)
        except CategoryNotFoundError:
            pass
        else:
            raise DuplicateCategorySlugError(f"Category slug '{request.slug}' already exists.")
        category = Category(
            id=self._id_generator.new_id(),
            parent_category_id=request.parent_category_id,
            category_key=request.category_key,
            name=request.name,
            slug=request.slug,
            description=request.description,
            is_active=True,
            sort_order=request.sort_order,
            created_at=self._clock.now(),
        )
        with self._uow:
            self._category_repo.add(category)
            self._uow.commit()
        return _to_result(category)
