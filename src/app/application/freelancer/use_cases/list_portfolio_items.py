from app.application.freelancer.dto import ListPortfolioItemsQuery, PortfolioItemResult
from app.application.freelancer.permissions import (
    PERMISSION_FREELANCER_READ_ANY,
    PERMISSION_FREELANCER_READ_OWN,
)
from app.application.shared.authorization import IAuthorizationService, authorize_owned_action
from app.application.shared.use_case import UseCase
from app.domain.freelancer.repositories import (
    IFreelancerProfileRepository,
    IPortfolioItemRepository,
)


class ListPortfolioItemsUseCase(UseCase[ListPortfolioItemsQuery, list[PortfolioItemResult]]):
    def __init__(
        self,
        authorization_service: IAuthorizationService,
        profile_repo: IFreelancerProfileRepository,
        portfolio_item_repo: IPortfolioItemRepository,
    ) -> None:
        self._authorization_service = authorization_service
        self._profile_repo = profile_repo
        self._portfolio_item_repo = portfolio_item_repo

    async def execute(self, request: ListPortfolioItemsQuery) -> list[PortfolioItemResult]:
        profile = await self._profile_repo.get_by_id(request.profile_id)
        await authorize_owned_action(
            self._authorization_service,
            request.actor_id,
            profile.user_id,
            PERMISSION_FREELANCER_READ_OWN,
            PERMISSION_FREELANCER_READ_ANY,
        )
        items = await self._portfolio_item_repo.list_by_profile(request.profile_id)
        return [
            PortfolioItemResult(
                item_id=item.id,
                freelancer_profile_id=item.freelancer_profile_id,
                title=item.title,
                description=item.description,
                external_url=item.external_url,
                file_asset_id=item.file_asset_id,
                display_order=item.display_order,
                is_featured=item.is_featured,
                deleted_at=item.deleted_at,
            )
            for item in sorted(items, key=lambda i: i.display_order)
        ]
