from app.domain.iam.entities import Role
from app.domain.iam.exceptions import RoleNotFoundError
from app.domain.iam.repositories import IRoleRepository
from app.domain.shared.types import EntityId


class FakeRoleRepository(IRoleRepository):
    async def __init__(self) -> None:
        self._store: dict[str, Role] = {}
        self._by_key: dict[str, Role] = {}

    async def add(self, role: Role) -> None:
        self._store[role.id] = role
        self._by_key[role.role_key] = role

    async def get_by_id(self, role_id: EntityId) -> Role:
        try:
            return self._store[role_id]
        except KeyError:
            raise RoleNotFoundError(f"Role {role_id} not found.") from None

    async def get_by_key(self, role_key: str) -> Role:
        try:
            return self._by_key[role_key]
        except KeyError:
            raise RoleNotFoundError(f"Role '{role_key}' not found.") from None

    async def list_all(self) -> list[Role]:
        return list(self._store.values())
