from dataclasses import dataclass
from datetime import datetime

from app.application.shared.exceptions import ValidationError
from app.domain.shared.types import EntityId


@dataclass(frozen=True)
class RegisterUserCommand:
    email: str
    password: str
    first_name: str
    last_name: str

    def validate(self) -> None:
        if not self.email.strip() or not self.password:
            raise ValidationError("email and password are required.")
        if not self.first_name.strip() or not self.last_name.strip():
            raise ValidationError("first_name and last_name are required.")


@dataclass(frozen=True)
class RegisterUserResult:
    user_id: EntityId
    email: str
    status: str
    created_at: datetime


@dataclass(frozen=True)
class LoginUserCommand:
    email: str
    password: str

    def validate(self) -> None:
        if not self.email.strip() or not self.password:
            raise ValidationError("email and password are required.")


@dataclass(frozen=True)
class LoginUserResult:
    user_id: EntityId
    email: str
    access_token: str
    refresh_token: str
    refresh_token_jti: str


@dataclass(frozen=True)
class LogoutUserCommand:
    refresh_token_jti: str


@dataclass(frozen=True)
class LogoutUserResult:
    user_id: EntityId


@dataclass(frozen=True)
class RefreshTokenCommand:
    raw_refresh_token: str


@dataclass(frozen=True)
class RefreshTokenResult:
    access_token: str
    refresh_token: str
    refresh_token_jti: str


@dataclass(frozen=True)
class ChangePasswordCommand:
    user_id: EntityId
    old_password: str
    new_password: str

    def validate(self) -> None:
        if not self.old_password or not self.new_password:
            raise ValidationError("old_password and new_password are required.")


@dataclass(frozen=True)
class ChangePasswordResult:
    user_id: EntityId
    password_changed_at: datetime


@dataclass(frozen=True)
class ForgotPasswordCommand:
    email: str

    def validate(self) -> None:
        if not self.email.strip():
            raise ValidationError("email is required.")


@dataclass(frozen=True)
class ForgotPasswordResult:
    email: str


@dataclass(frozen=True)
class BlockUserCommand:
    actor_id: EntityId
    target_user_id: EntityId
    reason: str


@dataclass(frozen=True)
class BlockUserResult:
    user_id: EntityId
    status: str


@dataclass(frozen=True)
class ActivateUserCommand:
    actor_id: EntityId
    target_user_id: EntityId


@dataclass(frozen=True)
class ActivateUserResult:
    user_id: EntityId
    status: str


@dataclass(frozen=True)
class AssignRoleCommand:
    actor_id: EntityId
    target_user_id: EntityId
    role_key: str


@dataclass(frozen=True)
class AssignRoleResult:
    user_role_id: EntityId
    user_id: EntityId
    role_id: EntityId


@dataclass(frozen=True)
class RemoveRoleCommand:
    actor_id: EntityId
    target_user_id: EntityId
    role_key: str


@dataclass(frozen=True)
class RemoveRoleResult:
    user_id: EntityId
    role_id: EntityId
    revoked_at: datetime


@dataclass(frozen=True)
class GrantPermissionCommand:
    actor_id: EntityId
    role_id: EntityId
    permission_id: EntityId


@dataclass(frozen=True)
class GrantPermissionResult:
    role_id: EntityId
    permission_id: EntityId


@dataclass(frozen=True)
class RevokePermissionCommand:
    actor_id: EntityId
    role_id: EntityId
    permission_id: EntityId


@dataclass(frozen=True)
class RevokePermissionResult:
    role_id: EntityId
    permission_id: EntityId
