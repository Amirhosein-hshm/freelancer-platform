from pydantic import BaseModel, Field


class RegisterRequest(BaseModel):
    email: str = Field(..., example="user@example.com")
    password: str = Field(..., min_length=8)
    first_name: str
    last_name: str


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


class ForgotPasswordRequest(BaseModel):
    email: str


class RegisterResponse(BaseModel):
    user_id: str
    email: str
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
    roles: list[str]
    permissions: list[str]