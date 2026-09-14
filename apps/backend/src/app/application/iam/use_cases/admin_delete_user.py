from app.application.iam.dto import AdminDeleteUserCommand, AdminDeleteUserResult
from app.application.shared.authorization import IAuthorizationService
from app.application.shared.ports import IClock, IUnitOfWork
from app.application.shared.use_case import UseCase
from app.domain.iam.exceptions import (
    CannotDeleteSelfError,
    LastAdminCannotBeDeletedError,
)
from app.domain.iam.repositories import IRoleRepository, IUserRepository, IUserRoleRepository

ADMIN_ROLE_KEY = "admin"


class AdminDeleteUserUseCase(UseCase[AdminDeleteUserCommand, AdminDeleteUserResult]):
    def __init__(
        self,
        authorization_service: IAuthorizationService,
        user_repo: IUserRepository,
        user_role_repo: IUserRoleRepository,
        role_repo: IRoleRepository,
        clock: IClock,
        uow: IUnitOfWork,
    ) -> None:
        self._authorization_service = authorization_service
        self._user_repo = user_repo
        self._user_role_repo = user_role_repo
        self._role_repo = role_repo
        self._clock = clock
        self._uow = uow

    async def execute(self, request: AdminDeleteUserCommand) -> AdminDeleteUserResult:
        await self._authorization_service.require_permission(request.actor_id, "user.delete")
        if request.actor_id == request.target_user_id:
            raise CannotDeleteSelfError(f"Admin {request.actor_id} cannot delete their own account.")
        user = await self._user_repo.get_by_id(request.target_user_id)
        target_roles = [role.role_key for role in await self._user_role_repo.list_active_roles_for_user(user.id)]
        if ADMIN_ROLE_KEY in target_roles:
            admin_role = await self._role_repo.get_by_key(ADMIN_ROLE_KEY)
            active_admins = await self._user_role_repo.list_active_user_ids_for_role(admin_role.id)
            if len(active_admins) <= 1:
                raise LastAdminCannotBeDeletedError(f"Cannot delete user {user.id}: it is the last active admin.")
        now = await self._clock.now()
        async with self._uow:
            user.soft_delete(now)
            await self._user_repo.update(user)
            await self._uow.commit()
        return AdminDeleteUserResult(user_id=user.id, deleted_at=now)
