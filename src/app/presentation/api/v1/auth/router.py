from fastapi import APIRouter, Depends

from app.application.iam.dto import (
    ChangePasswordCommand,
    ForgotPasswordCommand,
    LoginUserCommand,
    LogoutUserCommand,
    RefreshTokenCommand,
    RegisterUserCommand,
)
from app.application.iam.use_cases.change_password import ChangePasswordUseCase
from app.application.iam.use_cases.forgot_password import ForgotPasswordUseCase
from app.application.iam.use_cases.login_user import LoginUserUseCase
from app.application.iam.use_cases.logout_user import LogoutUserUseCase
from app.application.iam.use_cases.refresh_token import RefreshTokenUseCase
from app.application.iam.use_cases.register_user import RegisterUserUseCase
from app.application.shared.authorization import IAuthorizationService
from app.domain.iam.repositories import IUserRepository
from app.presentation.api.v1.auth.schemas import (
    ChangePasswordRequest,
    ForgotPasswordRequest,
    LoginRequest,
    LoginResponse,
    LogoutRequest,
    RefreshRequest,
    RefreshResponse,
    RegisterRequest,
    RegisterResponse,
    UserMeResponse,
)
from app.presentation.core.envelope import SuccessEnvelope
from app.presentation.core.providers import (
    get_authorization_service,
    get_change_password_use_case,
    get_forgot_password_use_case,
    get_login_user_use_case,
    get_logout_user_use_case,
    get_refresh_token_use_case,
    get_register_user_use_case,
    get_user_repository,
)
from app.presentation.core.security import get_current_user

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post(
    "/register",
    response_model=SuccessEnvelope[RegisterResponse],
    status_code=201,
    operation_id="register_user",
)
async def register(
    payload: RegisterRequest,
    use_case: RegisterUserUseCase = Depends(get_register_user_use_case),
) -> SuccessEnvelope[RegisterResponse]:
    result = await use_case.execute(
        RegisterUserCommand(
            email=payload.email,
            password=payload.password,
            first_name=payload.first_name,
            last_name=payload.last_name,
        )
    )
    return SuccessEnvelope(
        message="User registered.",
        data=RegisterResponse(
            user_id=result.user_id,
            email=result.email,
            status=result.status,
            created_at=result.created_at.isoformat(),
        ),
    )


@router.post("/login", response_model=SuccessEnvelope[LoginResponse], operation_id="login_user")
async def login(
    payload: LoginRequest,
    use_case: LoginUserUseCase = Depends(get_login_user_use_case),
) -> SuccessEnvelope[LoginResponse]:
    result = await use_case.execute(LoginUserCommand(email=payload.email, password=payload.password))
    return SuccessEnvelope(
        message="Login successful.",
        data=LoginResponse(
            user_id=result.user_id,
            email=result.email,
            access_token=result.access_token,
            refresh_token=result.refresh_token,
            refresh_token_jti=result.refresh_token_jti,
        ),
    )


@router.post("/refresh", response_model=SuccessEnvelope[RefreshResponse], operation_id="refresh_token")
async def refresh(
    payload: RefreshRequest,
    use_case: RefreshTokenUseCase = Depends(get_refresh_token_use_case),
) -> SuccessEnvelope[RefreshResponse]:
    result = await use_case.execute(RefreshTokenCommand(raw_refresh_token=payload.refresh_token))
    return SuccessEnvelope(
        message="Token refreshed.",
        data=RefreshResponse(
            access_token=result.access_token,
            refresh_token=result.refresh_token,
            refresh_token_jti=result.refresh_token_jti,
        ),
    )


@router.post("/logout", response_model=SuccessEnvelope[dict], operation_id="logout")
async def logout(
    payload: LogoutRequest,
    use_case: LogoutUserUseCase = Depends(get_logout_user_use_case),
) -> SuccessEnvelope[dict]:
    await use_case.execute(LogoutUserCommand(refresh_token_jti=payload.refresh_token))
    return SuccessEnvelope(message="Logged out.", data={})


@router.post("/change-password", response_model=SuccessEnvelope[dict], operation_id="change_password")
async def change_password(
    payload: ChangePasswordRequest,
    current_user=Depends(get_current_user),
    use_case: ChangePasswordUseCase = Depends(get_change_password_use_case),
) -> SuccessEnvelope[dict]:
    await use_case.execute(
        ChangePasswordCommand(
            user_id=current_user.user_id,
            old_password=payload.old_password,
            new_password=payload.new_password,
        )
    )
    return SuccessEnvelope(message="Password changed.", data={})


@router.post("/forgot-password", response_model=SuccessEnvelope[dict], operation_id="forgot_password")
async def forgot_password(
    payload: ForgotPasswordRequest,
    use_case: ForgotPasswordUseCase = Depends(get_forgot_password_use_case),
) -> SuccessEnvelope[dict]:
    await use_case.execute(ForgotPasswordCommand(email=payload.email))
    return SuccessEnvelope(message="If that email exists a reset was sent.", data={})


@router.get("/me", response_model=SuccessEnvelope[UserMeResponse], operation_id="get_me")
async def get_me(
    current_user=Depends(get_current_user),
    user_repository: IUserRepository = Depends(get_user_repository),
    authorization_service: IAuthorizationService = Depends(get_authorization_service),
) -> SuccessEnvelope[UserMeResponse]:
    user = await user_repository.get_by_id(current_user.user_id)
    permissions = await authorization_service.list_permissions_for_user(current_user.user_id)
    return SuccessEnvelope(
        message="Current user.",
        data=UserMeResponse(
            user_id=user.id,
            email=user.email.value,
            roles=current_user.roles,
            permissions=permissions,
        ),
    )