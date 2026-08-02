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
    def add(self, user: User) -> None: ...

    @abstractmethod
    def get_by_id(self, user_id: EntityId) -> User:
        """Raise ``UserNotFoundError`` if absent."""

    @abstractmethod
    def find_by_id(self, user_id: EntityId) -> User | None: ...

    @abstractmethod
    def get_by_email(self, email: Email) -> User:
        """Raise ``UserNotFoundError`` if absent."""

    @abstractmethod
    def exists_by_email(self, email: Email) -> bool: ...

    @abstractmethod
    def update(self, user: User) -> None: ...

    @abstractmethod
    def list_by_status(self, status: UserStatus, limit: int, offset: int) -> list[User]: ...


class IRoleRepository(ABC):
    @abstractmethod
    def get_by_id(self, role_id: EntityId) -> Role:
        """Raise ``RoleNotFoundError`` if absent."""

    @abstractmethod
    def get_by_key(self, role_key: str) -> Role:
        """Raise ``RoleNotFoundError`` if absent."""

    @abstractmethod
    def list_all(self) -> list[Role]: ...

    @abstractmethod
    def add(self, role: Role) -> None: ...


class IPermissionRepository(ABC):
    @abstractmethod
    def get_by_id(self, permission_id: EntityId) -> Permission:
        """Raise ``PermissionNotFoundError`` if absent."""

    @abstractmethod
    def list_by_module(self, module: str) -> list[Permission]: ...


class IUserRoleRepository(ABC):
    @abstractmethod
    def add(self, user_role: UserRole) -> None: ...

    @abstractmethod
    def find_active(self, user_id: EntityId, role_id: EntityId) -> UserRole | None: ...

    @abstractmethod
    def list_active_roles_for_user(self, user_id: EntityId) -> list[Role]: ...

    @abstractmethod
    def update(self, user_role: UserRole) -> None: ...


class IRolePermissionRepository(ABC):
    @abstractmethod
    def add(self, role_permission: RolePermission) -> None: ...

    @abstractmethod
    def list_permissions_for_role(self, role_id: EntityId) -> list[Permission]: ...

    @abstractmethod
    def remove(self, role_id: EntityId, permission_id: EntityId) -> None: ...


class IRefreshTokenRepository(ABC):
    @abstractmethod
    def add(self, token: RefreshToken) -> None: ...

    @abstractmethod
    def get_by_jti(self, jti: str) -> RefreshToken:
        """Raise ``RefreshTokenNotFoundError`` if absent."""

    @abstractmethod
    def find_by_token_hash(self, token_hash: str) -> RefreshToken | None:
        """Look a refresh token up by the hash of its raw value."""

    @abstractmethod
    def update(self, token: RefreshToken) -> None:
        """Persist a mutated token (revocation, rotation)."""

    @abstractmethod
    def revoke_all_for_user(self, user_id: EntityId, at: datetime) -> None: ...
