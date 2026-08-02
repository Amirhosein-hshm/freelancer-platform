from app.application.shared.authorization import IAuthorizationService
from app.application.shared.exceptions import PermissionDeniedError
from app.domain.shared.types import EntityId


class FakeAuthorizationService(IAuthorizationService):
    def __init__(self) -> None:
        self._permissions: dict[str, set[str]] = {}
        self._roles: dict[str, set[str]] = {}
        self.denied: list[str] = []

    def grant(self, user_id: EntityId, permission_key: str) -> None:
        self._permissions.setdefault(user_id, set()).add(permission_key)

    def assign_role(self, user_id: EntityId, role_key: str) -> None:
        self._roles.setdefault(user_id, set()).add(role_key)

    def has_permission(self, user_id: EntityId, permission_key: str) -> bool:
        return permission_key in self._permissions.get(user_id, set())

    def require_permission(self, user_id: EntityId, permission_key: str) -> None:
        if not self.has_permission(user_id, permission_key):
            self.denied.append(permission_key)
            raise PermissionDeniedError(
                f"User {user_id} does not have permission '{permission_key}'."
            )

    def has_role(self, user_id: EntityId, role_key: str) -> bool:
        return role_key in self._roles.get(user_id, set())
