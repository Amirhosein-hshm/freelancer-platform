from abc import ABC, abstractmethod
from datetime import datetime

from app.domain.iam.entities import (
    Permission,
    RefreshToken,
    Role,
    RolePermission,
    User,
    UserRole,
)
from app.domain.iam.enums import UserStatus
from app.domain.iam.value_objects import Email
from app.domain.shared.types import EntityId


class IUserRepository(ABC):
    @abstractmethod
    async def add(self, user: User) -> None: ...

    @abstractmethod
    async def get_by_id(self, user_id: EntityId) -> User:
        """Raise ``UserNotFoundError`` if absent."""

    @abstractmethod
    async def find_by_id(self, user_id: EntityId) -> User | None: ...

    @abstractmethod
    async def get_by_email(self, email: Email) -> User:
        """Raise ``UserNotFoundError`` if absent."""

    @abstractmethod
    async def exists_by_email(self, email: Email) -> bool: ...

    @abstractmethod
    async def update(self, user: User) -> None: ...

    @abstractmethod
    async def list_by_status(self, status: UserStatus, limit: int, offset: int) -> list[User]: ...


class IRoleRepository(ABC):
    @abstractmethod
    async def get_by_id(self, role_id: EntityId) -> Role:
        """Raise ``RoleNotFoundError`` if absent."""

    @abstractmethod
    async def get_by_key(self, role_key: str) -> Role:
        """Raise ``RoleNotFoundError`` if absent."""

    @abstractmethod
    async def list_all(self) -> list[Role]: ...

    @abstractmethod
    async def add(self, role: Role) -> None: ...


class IPermissionRepository(ABC):
    @abstractmethod
    async def get_by_id(self, permission_id: EntityId) -> Permission:
        """Raise ``PermissionNotFoundError`` if absent."""

    @abstractmethod
    async def list_by_module(self, module: str) -> list[Permission]: ...


class IUserRoleRepository(ABC):
    @abstractmethod
    async def add(self, user_role: UserRole) -> None: ...

    @abstractmethod
    async def find_active(self, user_id: EntityId, role_id: EntityId) -> UserRole | None: ...

    @abstractmethod
    async def list_active_roles_for_user(self, user_id: EntityId) -> list[Role]: ...

    @abstractmethod
    async def list_active_user_ids_for_role(self, role_id: EntityId) -> list[EntityId]: ...

    @abstractmethod
    async def update(self, user_role: UserRole) -> None: ...


class IRolePermissionRepository(ABC):
    @abstractmethod
    async def add(self, role_permission: RolePermission) -> None: ...

    @abstractmethod
    async def list_permissions_for_role(self, role_id: EntityId) -> list[Permission]: ...

    @abstractmethod
    async def remove(self, role_id: EntityId, permission_id: EntityId) -> None: ...


class IRefreshTokenRepository(ABC):
    @abstractmethod
    async def add(self, token: RefreshToken) -> None: ...

    @abstractmethod
    async def get_by_jti(self, jti: str) -> RefreshToken:
        """Raise ``RefreshTokenNotFoundError`` if absent."""

    @abstractmethod
    async def find_by_token_hash(self, token_hash: str) -> RefreshToken | None:
        """Look a refresh token up by the hash of its raw value."""

    @abstractmethod
    async def update(self, token: RefreshToken) -> None:
        """Persist a mutated token (revocation, rotation)."""

    @abstractmethod
    async def revoke_all_for_user(self, user_id: EntityId, at: datetime) -> None: ...
