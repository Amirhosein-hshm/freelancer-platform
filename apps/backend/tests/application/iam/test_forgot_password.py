import pytest

from app.application.iam.dto import ForgotPasswordCommand
from app.application.iam.use_cases.forgot_password import ForgotPasswordUseCase
from app.application.shared.exceptions import ValidationError
from app.domain.iam.exceptions import InvalidEmailError


def build_use_case(user_repo, id_generator, notification_service) -> ForgotPasswordUseCase:
    return ForgotPasswordUseCase(
        user_repo=user_repo, id_generator=id_generator, notification_service=notification_service
    )


class TestForgotPasswordUseCase:
    async def test_sends_reset_email(self, user_repo, id_generator, notification_service, make_user):
        await make_user(email="user@example.com")
        use_case = build_use_case(user_repo, id_generator, notification_service)

        result = await use_case.execute(ForgotPasswordCommand(email="user@example.com"))

        assert result.email == "user@example.com"
        assert notification_service.reset_tokens

    async def test_unknown_email_succeeds_silently(self, user_repo, id_generator, notification_service):
        use_case = build_use_case(user_repo, id_generator, notification_service)

        result = await use_case.execute(ForgotPasswordCommand(email="ghost@example.com"))

        assert result.email == "ghost@example.com"
        assert notification_service.reset_tokens == []
        assert not any(to == "ghost@example.com" for to, _subject, _body in notification_service.emails)

    async def test_invalid_email_raises(self, user_repo, id_generator, notification_service):
        use_case = build_use_case(user_repo, id_generator, notification_service)

        with pytest.raises(InvalidEmailError):
            await use_case.execute(ForgotPasswordCommand(email="not-an-email"))

    async def test_empty_email_raises_validation(self, user_repo, id_generator, notification_service):
        use_case = build_use_case(user_repo, id_generator, notification_service)

        with pytest.raises(ValidationError):
            await use_case.execute(ForgotPasswordCommand(email=""))
