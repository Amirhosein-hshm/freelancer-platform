from app.application.iam.dto import AdminListUsersQuery, AdminListUsersResult, AdminUserSummary
from app.application.shared.authorization import IAuthorizationService
from app.application.shared.pagination import limit_offset
from app.application.shared.use_case import UseCase
from app.domain.iam.repositories import IUserRepository


class AdminListUsersUseCase(UseCase[AdminListUsersQuery, AdminListUsersResult]):
    def __init__(
        self,
        authorization_service: IAuthorizationService,
        user_repo: IUserRepository,
    ) -> None:
        self._authorization_service = authorization_service
        self._user_repo = user_repo

    async def execute(self, request: AdminListUsersQuery) -> AdminListUsersResult:
        await self._authorization_service.require_permission(request.actor_id, "user.read")
        limit, offset = limit_offset(request.page, request.page_size)
        users = await self._user_repo.list_all(
            limit,
            offset,
            status=request.status,
            role=request.role,
            search=request.search,
        )
        total_items = await self._user_repo.count_all(request.status, request.role, request.search)
        return AdminListUsersResult(
            users=[
                AdminUserSummary(
                    user_id=user.id,
                    email=user.email.value,
                    first_name=user.first_name,
                    last_name=user.last_name,
                    status=user.status.value,
                    created_at=user.created_at,
                )
                for user in users
            ],
            total_items=total_items,
            page=request.page,
            page_size=request.page_size,
        )
