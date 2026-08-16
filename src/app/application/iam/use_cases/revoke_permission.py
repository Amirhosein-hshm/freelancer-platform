from app.application.iam.dto import RevokePermissionCommand, RevokePermissionResult
from app.application.shared.authorization import IAuthorizationService
from app.application.shared.ports import IUnitOfWork
from app.application.shared.use_case import UseCase
from app.domain.iam.exceptions import SystemRoleImmutableError
from app.domain.iam.repositories import (
    IPermissionRepository,
    IRolePermissionRepository,
    IRoleRepository,
)


class RevokePermissionUseCase(UseCase[RevokePermissionCommand, RevokePermissionResult]):
    def __init__(
        self,
        authorization_service: IAuthorizationService,
        role_repo: IRoleRepository,
        permission_repo: IPermissionRepository,
        role_permission_repo: IRolePermissionRepository,
        uow: IUnitOfWork,
    ) -> None:
        self._authorization_service = authorization_service
        self._role_repo = role_repo
        self._permission_repo = permission_repo
        self._role_permission_repo = role_permission_repo
        self._uow = uow

    async def execute(self, request: RevokePermissionCommand) -> RevokePermissionResult:
        await self._authorization_service.require_permission(request.actor_id, "user.revoke_permission")
        role = await self._role_repo.get_by_id(request.role_id)
        if role.is_system:
            raise SystemRoleImmutableError(f"Permissions of system role '{role.role_key}' cannot be revoked.")
        await self._permission_repo.get_by_id(request.permission_id)
        async with self._uow:
            await self._role_permission_repo.remove(request.role_id, request.permission_id)
            await self._uow.commit()
        return RevokePermissionResult(role_id=request.role_id, permission_id=request.permission_id)
