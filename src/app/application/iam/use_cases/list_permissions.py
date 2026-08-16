from app.application.iam.dto import (
    ListPermissionsQuery,
    ListPermissionsResult,
    PermissionSummary,
)
from app.application.shared.authorization import IAuthorizationService
from app.application.shared.use_case import UseCase
from app.domain.iam.repositories import IPermissionRepository

PERMISSION_IAM_READ = "user.read"


class ListPermissionsUseCase(UseCase[ListPermissionsQuery, ListPermissionsResult]):
    def __init__(
        self,
        authorization_service: IAuthorizationService,
        permission_repo: IPermissionRepository,
    ) -> None:
        self._authorization_service = authorization_service
        self._permission_repo = permission_repo

    async def execute(self, request: ListPermissionsQuery) -> ListPermissionsResult:
        await self._authorization_service.require_permission(request.actor_id, PERMISSION_IAM_READ)
        if request.module is not None:
            permissions = await self._permission_repo.list_by_module(request.module)
        else:
            permissions = await self._permission_repo.list_all()
        return ListPermissionsResult(
            permissions=[
                PermissionSummary(
                    permission_id=permission.id,
                    permission_key=permission.permission_key,
                    module=permission.module,
                    action=permission.action,
                    description=permission.description,
                    is_system=permission.is_system,
                )
                for permission in permissions
            ]
        )
