from app.application.freelancer.dto import (
    ListPortfolioItemsQuery,
    ListPortfolioItemsResult,
    PortfolioItemResult,
)
from app.application.freelancer.permissions import (
    PERMISSION_FREELANCER_READ_ANY,
    PERMISSION_FREELANCER_READ_OWN,
)
from app.application.shared.authorization import IAuthorizationService, authorize_owned_action
from app.application.shared.pagination import limit_offset
from app.application.shared.use_case import UseCase
from app.domain.freelancer.repositories import (
    IFreelancerProfileRepository,
    IPortfolioItemRepository,
)


class ListPortfolioItemsUseCase(UseCase[ListPortfolioItemsQuery, ListPortfolioItemsResult]):
    def __init__(
        self,
        authorization_service: IAuthorizationService,
        profile_repo: IFreelancerProfileRepository,
        portfolio_item_repo: IPortfolioItemRepository,
    ) -> None:
        self._authorization_service = authorization_service
        self._profile_repo = profile_repo
        self._portfolio_item_repo = portfolio_item_repo

    async def execute(self, request: ListPortfolioItemsQuery) -> ListPortfolioItemsResult:
        profile = await self._profile_repo.get_by_id(request.profile_id)
        await authorize_owned_action(
            self._authorization_service,
            request.actor_id,
            profile.user_id,
            PERMISSION_FREELANCER_READ_OWN,
            PERMISSION_FREELANCER_READ_ANY,
        )
        limit, offset = limit_offset(request.page, request.page_size)
        items = await self._portfolio_item_repo.list_by_profile(
            request.profile_id,
            limit=limit,
            offset=offset,
        )
        total_items = await self._portfolio_item_repo.count_by_profile(request.profile_id)
        return ListPortfolioItemsResult(
            items=[
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
                for item in items
            ],
            total_items=total_items,
            page=request.page,
            page_size=request.page_size,
        )