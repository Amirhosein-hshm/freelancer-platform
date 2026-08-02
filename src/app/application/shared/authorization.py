from abc import ABC, abstractmethod

from app.domain.shared.types import EntityId


class IAuthorizationService(ABC):
    @abstractmethod
    def has_permission(self, user_id: EntityId, permission_key: str) -> bool: ...

    @abstractmethod
    def require_permission(self, user_id: EntityId, permission_key: str) -> None:
        """Raise :class:`PermissionDeniedError` if the actor lacks the permission."""

    @abstractmethod
    def has_role(self, user_id: EntityId, role_key: str) -> bool: ...
