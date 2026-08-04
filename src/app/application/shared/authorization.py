from abc import ABC, abstractmethod

from app.domain.shared.types import EntityId


class IAuthorizationService(ABC):
    @abstractmethod
    async def has_permission(self, user_id: EntityId, permission_key: str) -> bool: ...

    @abstractmethod
    async def require_permission(self, user_id: EntityId, permission_key: str) -> None:
        """Raise :class:`PermissionDeniedError` if the actor lacks the permission."""

    @abstractmethod
    async def has_role(self, user_id: EntityId, role_key: str) -> bool: ...

    @abstractmethod
    async def list_permissions_for_user(self, user_id: EntityId) -> list[str]:
        """Return the union of all permission keys granted by the user's active roles."""


async def authorize_owned_action(
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
        await authz.require_permission(actor_id, own_permission)
    else:
        await authz.require_permission(actor_id, any_permission)
