from app.application.iam.dto import LogoutUserCommand, LogoutUserResult
from app.application.shared.ports import IClock, ITokenService, IUnitOfWork
from app.application.shared.use_case import UseCase
from app.domain.iam.exceptions import InvalidRefreshTokenError
from app.domain.iam.repositories import IRefreshTokenRepository


class LogoutUserUseCase(UseCase[LogoutUserCommand, LogoutUserResult]):
    def __init__(
        self,
        refresh_token_repo: IRefreshTokenRepository,
        token_service: ITokenService,
        clock: IClock,
        uow: IUnitOfWork,
    ) -> None:
        self._refresh_token_repo = refresh_token_repo
        self._token_service = token_service
        self._clock = clock
        self._uow = uow

    async def execute(self, request: LogoutUserCommand) -> LogoutUserResult:
        token_hash = await self._token_service.hash_refresh_token(request.raw_refresh_token)
        token = await self._refresh_token_repo.find_by_token_hash(token_hash)
        if token is None or not token.is_valid(await self._clock.now()):
            raise InvalidRefreshTokenError("Refresh token is invalid or has expired.")
        async with self._uow:
            token.revoke(await self._clock.now())
            await self._refresh_token_repo.update(token)
            await self._uow.commit()
        return LogoutUserResult(user_id=token.user_id)
