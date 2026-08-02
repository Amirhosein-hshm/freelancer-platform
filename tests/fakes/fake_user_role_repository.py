from app.domain.iam.entities import Role, UserRole
from app.domain.iam.repositories import IUserRoleRepository
from app.domain.shared.types import EntityId
from tests.fakes.fake_role_repository import FakeRoleRepository


class FakeUserRoleRepository(IUserRoleRepository):
    def __init__(self, role_repo: FakeRoleRepository | None = None) -> None:
        self._store: list[UserRole] = []
        self._role_repo = role_repo

    def add(self, user_role: UserRole) -> None:
        self._store.append(user_role)

    def find_active(self, user_id: EntityId, role_id: EntityId) -> UserRole | None:
        for user_role in self._store:
            if (
                user_role.user_id == user_id
                and user_role.role_id == role_id
                and user_role.is_active
            ):
                return user_role
        return None

    def list_active_roles_for_user(self, user_id: EntityId) -> list[Role]:
        role_ids = [
            ur.role_id for ur in self._store if ur.user_id == user_id and ur.is_active
        ]
        if self._role_repo is None:
            return []
        return [self._role_repo.get_by_id(role_id) for role_id in role_ids]

    def update(self, user_role: UserRole) -> None:
        for i, stored in enumerate(self._store):
            if stored.id == user_role.id:
                self._store[i] = user_role
                return
        self._store.append(user_role)
