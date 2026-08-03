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


def authorize_owned_action(
    authz: IAuthorizationService,
    actor_id: EntityId,
    owner_id: EntityId,
    own_permission: str,
    any_permission: str,
) -> None:
    """Grant ``own_permission`` to the resource owner, else require ``any_permission``.

    Implements the two-tier ownership permission convention (see AUTHORIZATION.md §3.1).
    """
    if actor_id == owner_id:
        authz.require_permission(actor_id, own_permission)
    else:
        authz.require_permission(actor_id, any_permission)