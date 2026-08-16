from dataclasses import dataclass
from datetime import datetime

from app.application.shared.exceptions import ValidationError
from app.domain.iam.enums import UserStatus
from app.domain.shared.types import EntityId


@dataclass(frozen=True)
class RegisterUserCommand:
    email: str
    password: str
    first_name: str
    last_name: str
    role: str

    def validate(self) -> None:
        if not self.email.strip() or not self.password:
            raise ValidationError("email and password are required.")
        if not self.first_name.strip() or not self.last_name.strip():
            raise ValidationError("first_name and last_name are required.")


@dataclass(frozen=True)
class RegisterUserResult:
    user_id: EntityId
    email: str
    role: str
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


@dataclass(frozen=True)
class AdminCreateUserCommand:
    actor_id: EntityId
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
class AdminCreateUserResult:
    user_id: EntityId
    email: str
    status: str
    created_at: datetime


@dataclass(frozen=True)
class AdminUpdateUserCommand:
    actor_id: EntityId
    target_user_id: EntityId
    first_name: str | None = None
    last_name: str | None = None
    phone: str | None = None

    def validate(self) -> None:
        if self.first_name is not None and not self.first_name.strip():
            raise ValidationError("first_name cannot be empty.")
        if self.last_name is not None and not self.last_name.strip():
            raise ValidationError("last_name cannot be empty.")


@dataclass(frozen=True)
class AdminUpdateUserResult:
    user_id: EntityId
    first_name: str
    last_name: str


@dataclass(frozen=True)
class AdminDeleteUserCommand:
    actor_id: EntityId
    target_user_id: EntityId


@dataclass(frozen=True)
class AdminDeleteUserResult:
    user_id: EntityId
    deleted_at: datetime


@dataclass(frozen=True)
class AdminGetUserQuery:
    actor_id: EntityId
    target_user_id: EntityId


@dataclass(frozen=True)
class AdminGetUserResult:
    user_id: EntityId
    email: str
    first_name: str
    last_name: str
    phone: str | None
    status: str
    email_verified_at: datetime | None
    phone_verified_at: datetime | None
    last_login_at: datetime | None
    roles: list[str]


@dataclass(frozen=True)
class AdminUserSummary:
    user_id: EntityId
    email: str
    first_name: str
    last_name: str
    status: str
    created_at: datetime


@dataclass(frozen=True)
class AdminListUsersQuery:
    actor_id: EntityId
    status: UserStatus | None = None
    page: int = 1
    page_size: int = 20


@dataclass(frozen=True)
class AdminListUsersResult:
    users: list[AdminUserSummary]
    total_items: int
    page: int
    page_size: int


@dataclass(frozen=True)
class RoleSummary:
    role_id: EntityId
    role_key: str
    name: str
    description: str | None
    is_system: bool


@dataclass(frozen=True)
class ListRolesQuery:
    actor_id: EntityId


@dataclass(frozen=True)
class ListRolesResult:
    roles: list[RoleSummary]


@dataclass(frozen=True)
class PermissionSummary:
    permission_id: EntityId
    permission_key: str
    module: str
    action: str
    description: str | None
    is_system: bool


@dataclass(frozen=True)
class ListPermissionsQuery:
    actor_id: EntityId
    module: str | None = None


@dataclass(frozen=True)
class ListPermissionsResult:
    permissions: list[PermissionSummary]
