from app.application.iam.dto import RemoveRoleCommand, RemoveRoleResult
from app.application.shared.authorization import IAuthorizationService
from app.application.shared.ports import IClock, IUnitOfWork
from app.application.shared.use_case import UseCase
from app.domain.iam.exceptions import LastAdminRoleRemovalError, UserRoleNotFoundError
from app.domain.iam.repositories import (
    IRoleRepository,
    IUserRepository,
    IUserRoleRepository,
)

ADMIN_ROLE_KEY = "admin"


class RemoveRoleUseCase(UseCase[RemoveRoleCommand, RemoveRoleResult]):
    def __init__(
        self,
        authorization_service: IAuthorizationService,
        user_repo: IUserRepository,
        role_repo: IRoleRepository,
        user_role_repo: IUserRoleRepository,
        clock: IClock,
        uow: IUnitOfWork,
    ) -> None:
        self._authorization_service = authorization_service
        self._user_repo = user_repo
        self._role_repo = role_repo
        self._user_role_repo = user_role_repo
        self._clock = clock
        self._uow = uow

    async def execute(self, request: RemoveRoleCommand) -> RemoveRoleResult:
        await self._authorization_service.require_permission(request.actor_id, "user.remove_role")
        user = await self._user_repo.get_by_id(request.target_user_id)
        role = await self._role_repo.get_by_key(request.role_key)
        user_role = await self._user_role_repo.find_active(user.id, role.id)
        if user_role is None:
            raise UserRoleNotFoundError(f"No active role '{role.role_key}' for user {user.id}.")
        if role.role_key == ADMIN_ROLE_KEY:
            active_admins = await self._user_role_repo.list_active_user_ids_for_role(role.id)
            if len(active_admins) <= 1:
                raise LastAdminRoleRemovalError(
                    f"Cannot remove role 'admin' from user {user.id}: it is the last active admin."
                )
        now = await self._clock.now()
        async with self._uow:
            user_role.revoke(now)
            await self._user_role_repo.update(user_role)
            await self._uow.commit()
        return RemoveRoleResult(user_id=user.id, role_id=role.id, revoked_at=now)
