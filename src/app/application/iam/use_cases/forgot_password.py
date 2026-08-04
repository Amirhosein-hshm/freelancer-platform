from app.application.iam.dto import ForgotPasswordCommand, ForgotPasswordResult
from app.application.shared.ports import IIdGenerator, INotificationService
from app.application.shared.use_case import UseCase
from app.domain.iam.repositories import IUserRepository
from app.domain.iam.value_objects import Email


class ForgotPasswordUseCase(UseCase[ForgotPasswordCommand, ForgotPasswordResult]):
    def __init__(
        self,
        user_repo: IUserRepository,
        id_generator: IIdGenerator,
        notification_service: INotificationService,
    ) -> None:
        self._user_repo = user_repo
        self._id_generator = id_generator
        self._notification_service = notification_service

    async def execute(self, request: ForgotPasswordCommand) -> ForgotPasswordResult:
        request.validate()
        email = Email(request.email)
        if await self._user_repo.exists_by_email(email):
            token = await self._id_generator.new_id()
            await self._notification_service.send_password_reset_email(email.value, token)
        return ForgotPasswordResult(email=email.value)
