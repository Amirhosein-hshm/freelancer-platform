from app.application.freelancer.dto import (
    DeletePortfolioItemCommand,
    DeletePortfolioItemResult,
)
from app.application.shared.ports import IClock, IUnitOfWork
from app.application.shared.use_case import UseCase
from app.domain.freelancer.exceptions import PortfolioItemNotFoundError
from app.domain.freelancer.repositories import (
    IFreelancerProfileRepository,
    IPortfolioItemRepository,
)


class DeletePortfolioItemUseCase(UseCase[DeletePortfolioItemCommand, DeletePortfolioItemResult]):
    """Soft-deletes the item; every portfolio read path filters ``deleted_at IS NULL``."""

    def __init__(
        self,
        profile_repo: IFreelancerProfileRepository,
        portfolio_item_repo: IPortfolioItemRepository,
        clock: IClock,
        uow: IUnitOfWork,
    ) -> None:
        self._profile_repo = profile_repo
        self._portfolio_item_repo = portfolio_item_repo
        self._clock = clock
        self._uow = uow

    async def execute(self, request: DeletePortfolioItemCommand) -> DeletePortfolioItemResult:
        profile = await self._profile_repo.get_by_user_id(request.user_id)
        item = await self._portfolio_item_repo.get_by_id(request.item_id)
        if item.freelancer_profile_id != profile.id:
            raise PortfolioItemNotFoundError(f"Portfolio item {request.item_id} not found for this profile.")
        now = await self._clock.now()
        async with self._uow:
            item.soft_delete(now)
            await self._portfolio_item_repo.update(item)
            await self._uow.commit()
        return DeletePortfolioItemResult(item_id=request.item_id)
