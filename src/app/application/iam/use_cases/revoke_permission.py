from app.application.iam.dto import RevokePermissionCommand, RevokePermissionResult
from app.application.shared.authorization import IAuthorizationService
from app.application.shared.ports import IUnitOfWork
from app.application.shared.use_case import UseCase
from app.domain.iam.repositories import IRolePermissionRepository


class RevokePermissionUseCase(UseCase[RevokePermissionCommand, RevokePermissionResult]):
    def __init__(
        self,
        authorization_service: IAuthorizationService,
        role_permission_repo: IRolePermissionRepository,
        uow: IUnitOfWork,
    ) -> None:
        self._authorization_service = authorization_service
        self._role_permission_repo = role_permission_repo
        self._uow = uow

    def execute(self, request: RevokePermissionCommand) -> RevokePermissionResult:
        self._authorization_service.require_permission(request.actor_id, "user.revoke_permission")
        with self._uow:
            self._role_permission_repo.remove(request.role_id, request.permission_id)
            self._uow.commit()
        return RevokePermissionResult(role_id=request.role_id, permission_id=request.permission_id)
