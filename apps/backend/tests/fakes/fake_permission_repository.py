from app.domain.iam.entities import Permission
from app.domain.iam.exceptions import PermissionNotFoundError
from app.domain.iam.repositories import IPermissionRepository
from app.domain.shared.types import EntityId


class FakePermissionRepository(IPermissionRepository):
    def __init__(self) -> None:
        self._store: dict[str, Permission] = {}

    async def add(self, permission: Permission) -> None:
        self._store[permission.id] = permission

    async def get_by_id(self, permission_id: EntityId) -> Permission:
        try:
            return self._store[permission_id]
        except KeyError:
            raise PermissionNotFoundError(f"Permission {permission_id} not found.") from None

    async def list_all(self) -> list[Permission]:
        return sorted(self._store.values(), key=lambda p: (p.module, p.permission_key))

    async def list_by_module(self, module: str) -> list[Permission]:
        return [p for p in self._store.values() if p.module == module]
