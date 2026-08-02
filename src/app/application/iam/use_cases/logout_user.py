from app.application.iam.dto import LogoutUserCommand, LogoutUserResult
from app.application.shared.ports import IClock, IUnitOfWork
from app.application.shared.use_case import UseCase
from app.domain.iam.repositories import IRefreshTokenRepository


class LogoutUserUseCase(UseCase[LogoutUserCommand, LogoutUserResult]):
    def __init__(
        self,
        refresh_token_repo: IRefreshTokenRepository,
        clock: IClock,
        uow: IUnitOfWork,
    ) -> None:
        self._refresh_token_repo = refresh_token_repo
        self._clock = clock
        self._uow = uow

    def execute(self, request: LogoutUserCommand) -> LogoutUserResult:
        token = self._refresh_token_repo.get_by_jti(request.refresh_token_jti)
        with self._uow:
            token.revoke(self._clock.now())
            self._refresh_token_repo.update(token)
            self._uow.commit()
        return LogoutUserResult(user_id=token.user_id)
