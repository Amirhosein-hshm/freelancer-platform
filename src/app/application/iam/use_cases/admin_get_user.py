from app.application.iam.dto import AdminGetUserQuery, AdminGetUserResult
from app.application.shared.authorization import IAuthorizationService
from app.application.shared.use_case import UseCase
from app.domain.iam.repositories import IUserRepository, IUserRoleRepository


class AdminGetUserUseCase(UseCase[AdminGetUserQuery, AdminGetUserResult]):
    def __init__(
        self,
        authorization_service: IAuthorizationService,
        user_repo: IUserRepository,
        user_role_repo: IUserRoleRepository,
    ) -> None:
        self._authorization_service = authorization_service
        self._user_repo = user_repo
        self._user_role_repo = user_role_repo

    async def execute(self, request: AdminGetUserQuery) -> AdminGetUserResult:
        await self._authorization_service.require_permission(request.actor_id, "user.read")
        user = await self._user_repo.get_by_id(request.target_user_id)
        roles = [
            role.role_key
            for role in await self._user_role_repo.list_active_roles_for_user(user.id)
        ]
        return AdminGetUserResult(
            user_id=user.id,
            email=user.email.value,
            first_name=user.first_name,
            last_name=user.last_name,
            phone=user.phone.value if user.phone else None,
            status=user.status.value,
            email_verified_at=user.email_verified_at,
            phone_verified_at=user.phone_verified_at,
            last_login_at=user.last_login_at,
            roles=roles,
        )