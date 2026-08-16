from app.application.freelancer.dto import (
    UpdatePortfolioItemCommand,
    UpdatePortfolioItemResult,
)
from app.application.shared.exceptions import ValidationError
from app.application.shared.ports import IFileStorageService
from app.application.shared.use_case import UseCase
from app.domain.freelancer.entities import PortfolioItem
from app.domain.freelancer.exceptions import PortfolioItemNotFoundError
from app.domain.freelancer.repositories import (
    IFreelancerProfileRepository,
    IPortfolioItemRepository,
)


class UpdatePortfolioItemUseCase(
    UseCase[UpdatePortfolioItemCommand, UpdatePortfolioItemResult]
):
    def __init__(
        self,
        profile_repo: IFreelancerProfileRepository,
        portfolio_item_repo: IPortfolioItemRepository,
        file_storage: IFileStorageService,
    ) -> None:
        self._profile_repo = profile_repo
        self._portfolio_item_repo = portfolio_item_repo
        self._file_storage = file_storage

    async def _owned_item(self, profile_id: str, item_id: str) -> PortfolioItem:
        item = await self._portfolio_item_repo.get_by_id(item_id)
        if item.freelancer_profile_id != profile_id:
            raise PortfolioItemNotFoundError(
                f"Portfolio item {item_id} not found for this profile."
            )
        return item

    async def execute(self, request: UpdatePortfolioItemCommand) -> UpdatePortfolioItemResult:
        request.validate()
        if request.file_asset_id is not None:
            try:
                await self._file_storage.get_metadata(request.file_asset_id)
            except (KeyError, FileNotFoundError) as exc:
                raise ValidationError(
                    f"File asset {request.file_asset_id} does not exist."
                ) from exc
        profile = await self._profile_repo.get_by_user_id(request.user_id)
        item = await self._owned_item(profile.id, request.item_id)
        item.title = request.title
        item.description = request.description
        item.external_url = request.external_url
        item.file_asset_id = request.file_asset_id
        item.display_order = request.display_order
        item.is_featured = request.is_featured
        await self._portfolio_item_repo.update(item)
        return UpdatePortfolioItemResult(item_id=item.id)
