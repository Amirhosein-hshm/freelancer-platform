from app.application.iam.dto import (
    AdminUpdateUserCommand,
    AdminUpdateUserResult,
)
from app.application.shared.authorization import IAuthorizationService
from app.application.shared.ports import IUnitOfWork
from app.application.shared.use_case import UseCase
from app.domain.iam.repositories import IUserRepository
from app.domain.iam.value_objects import PhoneNumber


class AdminUpdateUserUseCase(UseCase[AdminUpdateUserCommand, AdminUpdateUserResult]):
    def __init__(
        self,
        authorization_service: IAuthorizationService,
        user_repo: IUserRepository,
        uow: IUnitOfWork,
    ) -> None:
        self._authorization_service = authorization_service
        self._user_repo = user_repo
        self._uow = uow

    async def execute(self, request: AdminUpdateUserCommand) -> AdminUpdateUserResult:
        await self._authorization_service.require_permission(request.actor_id, "user.update_any")
        request.validate()
        user = await self._user_repo.get_by_id(request.target_user_id)
        if request.first_name is not None:
            user.first_name = request.first_name
        if request.last_name is not None:
            user.last_name = request.last_name
        if request.phone is not None:
            user.phone = PhoneNumber(request.phone)
        async with self._uow:
            await self._user_repo.update(user)
            await self._uow.commit()
        return AdminUpdateUserResult(
            user_id=user.id,
            first_name=user.first_name,
            last_name=user.last_name,
        )
