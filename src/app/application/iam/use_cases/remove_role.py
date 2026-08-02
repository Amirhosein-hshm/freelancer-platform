from app.application.iam.dto import RemoveRoleCommand, RemoveRoleResult
from app.application.shared.authorization import IAuthorizationService
from app.application.shared.ports import IClock, IUnitOfWork
from app.application.shared.use_case import UseCase
from app.domain.iam.exceptions import UserRoleNotFoundError
from app.domain.iam.repositories import (
    IRoleRepository,
    IUserRepository,
    IUserRoleRepository,
)


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

    def execute(self, request: RemoveRoleCommand) -> RemoveRoleResult:
        self._authorization_service.require_permission(request.actor_id, "user.remove_role")
        user = self._user_repo.get_by_id(request.target_user_id)
        role = self._role_repo.get_by_key(request.role_key)
        user_role = self._user_role_repo.find_active(user.id, role.id)
        if user_role is None:
            raise UserRoleNotFoundError(
                f"No active role '{role.role_key}' for user {user.id}."
            )
        now = self._clock.now()
        with self._uow:
            user_role.revoke(now)
            self._user_role_repo.update(user_role)
            self._uow.commit()
        return RemoveRoleResult(user_id=user.id, role_id=role.id, revoked_at=now)
