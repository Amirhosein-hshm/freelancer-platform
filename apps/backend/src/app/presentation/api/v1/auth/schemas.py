from pydantic import BaseModel, Field


class RegisterRequest(BaseModel):
    email: str = Field(..., example="user@example.com")
    password: str = Field(..., min_length=8)
    first_name: str
    last_name: str
    role: str = Field(..., example="customer")


class LoginRequest(BaseModel):
    email: str
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str


class LogoutRequest(BaseModel):
    refresh_token: str


class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str = Field(..., min_length=8)


class UpdateOwnProfileRequest(BaseModel):
    first_name: str | None = None
    last_name: str | None = None
    phone: str | None = None


class ForgotPasswordRequest(BaseModel):
    email: str


class RegisterResponse(BaseModel):
    user_id: str
    email: str
    role: str
    status: str
    created_at: str


class LoginResponse(BaseModel):
    user_id: str
    email: str
    access_token: str
    refresh_token: str
    refresh_token_jti: str


class RefreshResponse(BaseModel):
    access_token: str
    refresh_token: str
    refresh_token_jti: str


class UserMeResponse(BaseModel):
    user_id: str
    email: str
    first_name: str
    last_name: str
    phone: str | None = None
    roles: list[str]
    permissions: list[str]
    freelancer_profile_id: str | None = None
    freelancer_onboarding_needed: bool = False
    freelancer_approval_status: str | None = None
    freelancer_level: str | None = None
