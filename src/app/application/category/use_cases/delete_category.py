from app.application.category.dto import DeleteCategoryCommand, DeleteCategoryResult
from app.application.category.use_cases.create_category import PERMISSION_CATEGORY_MANAGE
from app.application.shared.authorization import IAuthorizationService
from app.application.shared.ports import IClock, IUnitOfWork
from app.application.shared.use_case import UseCase
from app.domain.category.repositories import ICategoryRepository


class DeleteCategoryUseCase(UseCase[DeleteCategoryCommand, DeleteCategoryResult]):
    def __init__(
        self,
        authorization_service: IAuthorizationService,
        category_repo: ICategoryRepository,
        clock: IClock,
        uow: IUnitOfWork,
    ) -> None:
        self._authorization_service = authorization_service
        self._category_repo = category_repo
        self._clock = clock
        self._uow = uow

    async def execute(self, request: DeleteCategoryCommand) -> DeleteCategoryResult:
        await self._authorization_service.require_permission(
            request.actor_id, PERMISSION_CATEGORY_MANAGE
        )
        category = await self._category_repo.get_by_id(request.category_id)
        async with self._uow:
            category.soft_delete(await self._clock.now())
            await self._category_repo.update(category)
            await self._uow.commit()
        return DeleteCategoryResult(category_id=category.id)
