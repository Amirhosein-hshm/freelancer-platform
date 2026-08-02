from app.application.iam.dto import GrantPermissionCommand, GrantPermissionResult
from app.application.shared.authorization import IAuthorizationService
from app.application.shared.ports import IClock, IIdGenerator, IUnitOfWork
from app.application.shared.use_case import UseCase
from app.domain.iam.entities import RolePermission
from app.domain.iam.repositories import (
    IPermissionRepository,
    IRolePermissionRepository,
    IRoleRepository,
)


class GrantPermissionUseCase(UseCase[GrantPermissionCommand, GrantPermissionResult]):
    def __init__(
        self,
        authorization_service: IAuthorizationService,
        role_repo: IRoleRepository,
        permission_repo: IPermissionRepository,
        role_permission_repo: IRolePermissionRepository,
        id_generator: IIdGenerator,
        clock: IClock,
        uow: IUnitOfWork,
    ) -> None:
        self._authorization_service = authorization_service
        self._role_repo = role_repo
        self._permission_repo = permission_repo
        self._role_permission_repo = role_permission_repo
        self._id_generator = id_generator
        self._clock = clock
        self._uow = uow

    def execute(self, request: GrantPermissionCommand) -> GrantPermissionResult:
        self._authorization_service.require_permission(request.actor_id, "user.grant_permission")
        role = self._role_repo.get_by_id(request.role_id)
        permission = self._permission_repo.get_by_id(request.permission_id)
        now = self._clock.now()
        role_permission = RolePermission(
            id=self._id_generator.new_id(),
            role_id=role.id,
            permission_id=permission.id,
            granted_by_user_id=request.actor_id,
            granted_at=now,
            created_at=now,
        )
        with self._uow:
            self._role_permission_repo.add(role_permission)
            self._uow.commit()
        return GrantPermissionResult(role_id=role.id, permission_id=permission.id)
