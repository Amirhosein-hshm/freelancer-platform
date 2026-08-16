from app.application.iam.dto import ListRolesQuery, ListRolesResult, RoleSummary
from app.application.shared.authorization import IAuthorizationService
from app.application.shared.use_case import UseCase
from app.domain.iam.repositories import IRoleRepository

PERMISSION_IAM_READ = "user.read"


class ListRolesUseCase(UseCase[ListRolesQuery, ListRolesResult]):
    def __init__(
        self,
        authorization_service: IAuthorizationService,
        role_repo: IRoleRepository,
    ) -> None:
        self._authorization_service = authorization_service
        self._role_repo = role_repo

    async def execute(self, request: ListRolesQuery) -> ListRolesResult:
        await self._authorization_service.require_permission(request.actor_id, PERMISSION_IAM_READ)
        roles = await self._role_repo.list_all()
        return ListRolesResult(
            roles=[
                RoleSummary(
                    role_id=role.id,
                    role_key=role.role_key,
                    name=role.name,
                    description=role.description,
                    is_system=role.is_system,
                )
                for role in roles
            ]
        )
