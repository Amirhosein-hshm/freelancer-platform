from app.application.freelancer.dto import (
    AddPortfolioItemCommand,
    AddPortfolioItemResult,
)
from app.application.shared.exceptions import ValidationError
from app.application.shared.ports import IClock, IFileStorageService, IIdGenerator, IUnitOfWork
from app.application.shared.use_case import UseCase
from app.domain.freelancer.entities import PortfolioItem
from app.domain.freelancer.repositories import (
    IFreelancerProfileRepository,
    IPortfolioItemRepository,
)


class AddPortfolioItemUseCase(UseCase[AddPortfolioItemCommand, AddPortfolioItemResult]):
    def __init__(
        self,
        profile_repo: IFreelancerProfileRepository,
        portfolio_item_repo: IPortfolioItemRepository,
        file_storage: IFileStorageService,
        id_generator: IIdGenerator,
        clock: IClock,
        uow: IUnitOfWork,
    ) -> None:
        self._profile_repo = profile_repo
        self._portfolio_item_repo = portfolio_item_repo
        self._file_storage = file_storage
        self._id_generator = id_generator
        self._clock = clock
        self._uow = uow

    async def execute(self, request: AddPortfolioItemCommand) -> AddPortfolioItemResult:
        request.validate()
        if request.file_asset_id is not None:
            try:
                await self._file_storage.get_metadata(request.file_asset_id)
            except (KeyError, FileNotFoundError) as exc:
                raise ValidationError(f"File asset {request.file_asset_id} does not exist.") from exc
        profile = await self._profile_repo.get_by_user_id(request.user_id)
        now = await self._clock.now()
        item = PortfolioItem(
            id=await self._id_generator.new_id(),
            freelancer_profile_id=profile.id,
            title=request.title,
            description=request.description,
            external_url=request.external_url,
            file_asset_id=request.file_asset_id,
            display_order=request.display_order,
            is_featured=request.is_featured,
            deleted_at=None,
            created_at=now,
        )
        async with self._uow:
            await self._portfolio_item_repo.add(item)
            await self._uow.commit()
        return AddPortfolioItemResult(item_id=item.id)
