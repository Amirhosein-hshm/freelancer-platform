from pydantic import BaseModel, Field


class AdminCreateUserRequest(BaseModel):
    email: str = Field(..., example="user@example.com")
    password: str = Field(..., min_length=8)
    first_name: str
    last_name: str


class AdminCreateUserResponse(BaseModel):
    user_id: str
    email: str
    status: str
    created_at: str


class AdminUpdateUserRequest(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    phone: str | None = None


class AdminUpdateUserResponse(BaseModel):
    user_id: str
    first_name: str
    last_name: str


class AdminDeleteUserResponse(BaseModel):
    user_id: str
    deleted_at: str


class ActivateUserResponse(BaseModel):
    user_id: str
    status: str


class BlockUserRequest(BaseModel):
    reason: str


class BlockUserResponse(BaseModel):
    user_id: str
    status: str


class AssignRoleRequest(BaseModel):
    role_key: str


class AssignRoleResponse(BaseModel):
    user_role_id: str
    user_id: str
    role_id: str


class RemoveRoleResponse(BaseModel):
    user_id: str
    role_id: str
    revoked_at: str


class GrantPermissionRequest(BaseModel):
    permission_id: str


class GrantPermissionResponse(BaseModel):
    role_id: str
    permission_id: str


class RevokePermissionResponse(BaseModel):
    role_id: str
    permission_id: str


class AdminGetUserResponse(BaseModel):
    user_id: str
    email: str
    first_name: str
    last_name: str
    phone: str | None = None
    status: str
    email_verified_at: str | None = None
    phone_verified_at: str | None = None
    last_login_at: str | None = None
    roles: list[str]


class AdminUserSummaryResponse(BaseModel):
    user_id: str
    email: str
    first_name: str
    last_name: str
    status: str
    created_at: str


class RelatedUserResponse(BaseModel):
    user_id: str
    email: str
    first_name: str
    last_name: str


class AdminListUsersResponse(BaseModel):
    users: list[AdminUserSummaryResponse]


class RoleResponse(BaseModel):
    role_id: str
    role_key: str
    name: str
    description: str | None = None
    is_system: bool


class ListRolesResponse(BaseModel):
    roles: list[RoleResponse]


class PermissionResponse(BaseModel):
    permission_id: str
    permission_key: str
    module: str
    action: str
    description: str | None = None
    is_system: bool


class ListPermissionsResponse(BaseModel):
    permissions: list[PermissionResponse]
