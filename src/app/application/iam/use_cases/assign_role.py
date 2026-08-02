from app.application.iam.dto import AssignRoleCommand, AssignRoleResult
from app.application.shared.authorization import IAuthorizationService
from app.application.shared.ports import IClock, IIdGenerator, IUnitOfWork
from app.application.shared.use_case import UseCase
from app.domain.iam.entities import UserRole
from app.domain.iam.exceptions import RoleAlreadyAssignedError
from app.domain.iam.repositories import (
    IRoleRepository,
    IUserRepository,
    IUserRoleRepository,
)


class AssignRoleUseCase(UseCase[AssignRoleCommand, AssignRoleResult]):
    def __init__(
        self,
        authorization_service: IAuthorizationService,
        user_repo: IUserRepository,
        role_repo: IRoleRepository,
        user_role_repo: IUserRoleRepository,
        id_generator: IIdGenerator,
        clock: IClock,
        uow: IUnitOfWork,
    ) -> None:
        self._authorization_service = authorization_service
        self._user_repo = user_repo
        self._role_repo = role_repo
        self._user_role_repo = user_role_repo
        self._id_generator = id_generator
        self._clock = clock
        self._uow = uow

    def execute(self, request: AssignRoleCommand) -> AssignRoleResult:
        self._authorization_service.require_permission(request.actor_id, "user.assign_role")
        user = self._user_repo.get_by_id(request.target_user_id)
        role = self._role_repo.get_by_key(request.role_key)
        if self._user_role_repo.find_active(user.id, role.id) is not None:
            raise RoleAlreadyAssignedError(
                f"Role '{role.role_key}' is already assigned to user {user.id}."
            )
        now = self._clock.now()
        user_role = UserRole(
            id=self._id_generator.new_id(),
            user_id=user.id,
            role_id=role.id,
            assigned_by_user_id=request.actor_id,
            assigned_at=now,
            created_at=now,
        )
        with self._uow:
            self._user_role_repo.add(user_role)
            self._uow.commit()
        return AssignRoleResult(
            user_role_id=user_role.id,
            user_id=user.id,
            role_id=role.id,
        )
