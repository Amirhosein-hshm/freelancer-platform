from datetime import timedelta

from app.application.iam.dto import RefreshTokenCommand, RefreshTokenResult
from app.application.shared.ports import (
    IClock,
    IIdGenerator,
    ITokenService,
    IUnitOfWork,
)
from app.application.shared.use_case import UseCase
from app.domain.iam.entities import RefreshToken
from app.domain.iam.exceptions import InvalidRefreshTokenError, UserNotActiveError
from app.domain.iam.repositories import (
    IRefreshTokenRepository,
    IUserRepository,
    IUserRoleRepository,
)

REFRESH_TOKEN_TTL = timedelta(days=30)


class RefreshTokenUseCase(UseCase[RefreshTokenCommand, RefreshTokenResult]):
    def __init__(
        self,
        refresh_token_repo: IRefreshTokenRepository,
        user_repo: IUserRepository,
        user_role_repo: IUserRoleRepository,
        token_service: ITokenService,
        id_generator: IIdGenerator,
        clock: IClock,
        uow: IUnitOfWork,
    ) -> None:
        self._refresh_token_repo = refresh_token_repo
        self._user_repo = user_repo
        self._user_role_repo = user_role_repo
        self._token_service = token_service
        self._id_generator = id_generator
        self._clock = clock
        self._uow = uow

    async def execute(self, request: RefreshTokenCommand) -> RefreshTokenResult:
        token_hash = await self._token_service.hash_refresh_token(request.raw_refresh_token)
        token = await self._refresh_token_repo.find_by_token_hash(token_hash)
        if token is None or not token.is_valid(await self._clock.now()):
            raise InvalidRefreshTokenError("Refresh token is invalid or has expired.")
        user = await self._user_repo.get_by_id(token.user_id)
        if not user.is_active():
            raise UserNotActiveError(f"User {user.id} is not active.")
        roles = [
            role.role_key for role in await self._user_role_repo.list_active_roles_for_user(user.id)
        ]
        access_token = await self._token_service.generate_access_token(user.id, roles)
        now = await self._clock.now()
        new_raw, new_jti = await self._token_service.generate_refresh_token()
        new_token = RefreshToken(
            id=await self._id_generator.new_id(),
            user_id=user.id,
            jti=new_jti,
            token_hash=await self._token_service.hash_refresh_token(new_raw),
            issued_at=now,
            expires_at=now + REFRESH_TOKEN_TTL,
            created_at=now,
        )
        async with self._uow:
            token.revoke(now, replaced_by=new_token.id)
            await self._refresh_token_repo.update(token)
            await self._refresh_token_repo.add(new_token)
            await self._uow.commit()
        return RefreshTokenResult(
            access_token=access_token,
            refresh_token=new_raw,
            refresh_token_jti=new_jti,
        )
