from app.domain.iam.entities import Permission, RolePermission
from app.domain.iam.repositories import IRolePermissionRepository
from app.domain.shared.types import EntityId
from tests.fakes.fake_permission_repository import FakePermissionRepository


class FakeRolePermissionRepository(IRolePermissionRepository):
    def __init__(self, permission_repo: FakePermissionRepository | None = None) -> None:
        self._store: list[RolePermission] = []
        self._permission_repo = permission_repo

    def add(self, role_permission: RolePermission) -> None:
        self._store.append(role_permission)

    def list_permissions_for_role(self, role_id: EntityId) -> list[Permission]:
        permission_ids = [
            rp.permission_id for rp in self._store if rp.role_id == role_id
        ]
        if self._permission_repo is None:
            return []
        return [self._permission_repo.get_by_id(permission_id) for permission_id in permission_ids]

    def remove(self, role_id: EntityId, permission_id: EntityId) -> None:
        self._store = [
            rp
            for rp in self._store
            if not (rp.role_id == role_id and rp.permission_id == permission_id)
        ]
