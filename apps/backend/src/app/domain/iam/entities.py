from dataclasses import dataclass
from datetime import datetime

from app.domain.iam.enums import UserStatus
from app.domain.iam.exceptions import UserAlreadyBlockedError
from app.domain.iam.value_objects import Email, PasswordHash, PhoneNumber
from app.domain.shared.entity import AggregateRoot, Entity
from app.domain.shared.exceptions import InvalidStateTransitionError
from app.domain.shared.types import EntityId


@dataclass(eq=False)
class User(AggregateRoot):
    email: Email
    phone: PhoneNumber | None
    password_hash: PasswordHash
    first_name: str
    last_name: str
    status: UserStatus
    email_verified_at: datetime | None = None
    phone_verified_at: datetime | None = None
    last_login_at: datetime | None = None
    password_changed_at: datetime | None = None
    deleted_at: datetime | None = None

    def activate(self) -> None:
        """PENDING/BLOCKED -> ACTIVE; ARCHIVED users can never be re-activated."""
        if self.status == UserStatus.ARCHIVED:
            raise InvalidStateTransitionError(f"Cannot activate user {self.id}: user is ARCHIVED.")
        if self.status == UserStatus.ACTIVE:
            return
        self.status = UserStatus.ACTIVE

    def block(self, reason: str) -> None:
        """ACTIVE/PENDING -> BLOCKED; rejects ARCHIVED users."""
        if self.status == UserStatus.ARCHIVED:
            raise InvalidStateTransitionError(f"Cannot block user {self.id}: user is ARCHIVED.")
        if self.status == UserStatus.BLOCKED:
            raise UserAlreadyBlockedError(f"User {self.id} is already blocked.")
        self.status = UserStatus.BLOCKED

    def record_login(self, at: datetime) -> None:
        self.last_login_at = at

    def change_password(self, new_hash: PasswordHash, at: datetime) -> None:
        self.password_hash = new_hash
        self.password_changed_at = at

    def soft_delete(self, at: datetime) -> None:
        self.deleted_at = at

    def is_active(self) -> bool:
        return self.status == UserStatus.ACTIVE and self.deleted_at is None


@dataclass(eq=False)
class Role(Entity):
    role_key: str
    name: str
    description: str | None = None
    is_system: bool = False

    def rename(self, name: str) -> None:
        """System roles can be renamed, but their immutable key never changes."""
        self.name = name


@dataclass(eq=False)
class Permission(Entity):
    permission_key: str
    module: str
    action: str
    description: str | None = None
    is_system: bool = False


@dataclass(eq=False)
class UserRole(Entity):
    user_id: EntityId
    role_id: EntityId
    assigned_by_user_id: EntityId
    assigned_at: datetime
    revoked_at: datetime | None = None
    is_active: bool = True

    def revoke(self, at: datetime) -> None:
        if not self.is_active:
            raise InvalidStateTransitionError(f"UserRole {self.id} is already revoked.")
        self.is_active = False
        self.revoked_at = at


@dataclass(eq=False)
class RolePermission(Entity):
    role_id: EntityId
    permission_id: EntityId
    granted_by_user_id: EntityId
    granted_at: datetime


@dataclass(eq=False)
class RefreshToken(Entity):
    user_id: EntityId
    jti: str
    token_hash: str
    issued_at: datetime
    expires_at: datetime
    device_name: str | None = None
    ip_address: str | None = None
    user_agent: str | None = None
    revoked_at: datetime | None = None
    replaced_by_token_id: EntityId | None = None

    def is_valid(self, now: datetime) -> bool:
        return self.revoked_at is None and self.expires_at > now

    def revoke(self, at: datetime, replaced_by: EntityId | None = None) -> None:
        self.revoked_at = at
        self.replaced_by_token_id = replaced_by
