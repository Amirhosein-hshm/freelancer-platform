from app.application.iam.dto import BlockUserCommand, BlockUserResult
from app.application.shared.authorization import IAuthorizationService
from app.application.shared.ports import IClock, IUnitOfWork
from app.application.shared.use_case import UseCase
from app.domain.iam.repositories import IUserRepository


class BlockUserUseCase(UseCase[BlockUserCommand, BlockUserResult]):
    def __init__(
        self,
        authorization_service: IAuthorizationService,
        user_repo: IUserRepository,
        clock: IClock,
        uow: IUnitOfWork,
    ) -> None:
        self._authorization_service = authorization_service
        self._user_repo = user_repo
        self._clock = clock
        self._uow = uow

    async def execute(self, request: BlockUserCommand) -> BlockUserResult:
        await self._authorization_service.require_permission(request.actor_id, "user.block")
        user = await self._user_repo.get_by_id(request.target_user_id)
        async with self._uow:
            user.block(request.reason)
            await self._user_repo.update(user)
            await self._uow.commit()
        return BlockUserResult(user_id=user.id, status=user.status.value)
