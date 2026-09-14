from datetime import timedelta

from app.application.iam.dto import LoginUserCommand, LoginUserResult
from app.application.shared.ports import (
    IClock,
    IIdGenerator,
    IPasswordHasher,
    ITokenService,
    IUnitOfWork,
)
from app.application.shared.use_case import UseCase
from app.domain.iam.entities import RefreshToken
from app.domain.iam.enums import UserStatus
from app.domain.iam.exceptions import (
    InvalidCredentialsError,
    UserNotActiveError,
    UserNotFoundError,
)
from app.domain.iam.repositories import (
    IRefreshTokenRepository,
    IUserRepository,
    IUserRoleRepository,
)
from app.domain.iam.value_objects import Email

REFRESH_TOKEN_TTL = timedelta(days=30)


class LoginUserUseCase(UseCase[LoginUserCommand, LoginUserResult]):
    def __init__(
        self,
        user_repo: IUserRepository,
        user_role_repo: IUserRoleRepository,
        refresh_token_repo: IRefreshTokenRepository,
        password_hasher: IPasswordHasher,
        token_service: ITokenService,
        id_generator: IIdGenerator,
        clock: IClock,
        uow: IUnitOfWork,
    ) -> None:
        self._user_repo = user_repo
        self._user_role_repo = user_role_repo
        self._refresh_token_repo = refresh_token_repo
        self._password_hasher = password_hasher
        self._token_service = token_service
        self._id_generator = id_generator
        self._clock = clock
        self._uow = uow

    async def execute(self, request: LoginUserCommand) -> LoginUserResult:
        request.validate()
        email = Email(request.email)
        try:
            user = await self._user_repo.get_by_email(email)
        except UserNotFoundError:
            raise InvalidCredentialsError(f"Invalid credentials for {email.value}.") from None
        if not await self._password_hasher.verify(request.password, user.password_hash.value):
            raise InvalidCredentialsError(f"Invalid credentials for {email.value}.")
        if user.status != UserStatus.ACTIVE:
            raise UserNotActiveError(f"User {user.id} is not active (status={user.status.value}).")
        roles = [role.role_key for role in await self._user_role_repo.list_active_roles_for_user(user.id)]
        access_token = await self._token_service.generate_access_token(user.id, roles)
        raw_token, jti = await self._token_service.generate_refresh_token()
        now = await self._clock.now()
        refresh_token = RefreshToken(
            id=await self._id_generator.new_id(),
            user_id=user.id,
            jti=jti,
            token_hash=await self._token_service.hash_refresh_token(raw_token),
            issued_at=now,
            expires_at=now + REFRESH_TOKEN_TTL,
            created_at=now,
        )
        async with self._uow:
            await self._refresh_token_repo.add(refresh_token)
            user.record_login(now)
            await self._user_repo.update(user)
            await self._uow.commit()
        return LoginUserResult(
            user_id=user.id,
            email=email.value,
            access_token=access_token,
            refresh_token=raw_token,
            refresh_token_jti=jti,
        )
