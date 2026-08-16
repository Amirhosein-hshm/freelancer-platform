from app.application.freelancer.dto import (
    DeletePortfolioItemCommand,
    DeletePortfolioItemResult,
)
from app.application.shared.use_case import UseCase
from app.domain.freelancer.exceptions import PortfolioItemNotFoundError
from app.domain.freelancer.repositories import (
    IFreelancerProfileRepository,
    IPortfolioItemRepository,
)


class DeletePortfolioItemUseCase(UseCase[DeletePortfolioItemCommand, DeletePortfolioItemResult]):
    def __init__(
        self,
        profile_repo: IFreelancerProfileRepository,
        portfolio_item_repo: IPortfolioItemRepository,
    ) -> None:
        self._profile_repo = profile_repo
        self._portfolio_item_repo = portfolio_item_repo

    async def execute(self, request: DeletePortfolioItemCommand) -> DeletePortfolioItemResult:
        profile = await self._profile_repo.get_by_user_id(request.user_id)
        item = await self._portfolio_item_repo.get_by_id(request.item_id)
        if item.freelancer_profile_id != profile.id:
            raise PortfolioItemNotFoundError(f"Portfolio item {request.item_id} not found for this profile.")
        await self._portfolio_item_repo.delete(request.item_id)
        return DeletePortfolioItemResult(item_id=request.item_id)
