import pytest

from app.application.iam.dto import RegisterUserCommand
from app.application.iam.use_cases.register_user import RegisterUserUseCase
from app.application.shared.exceptions import ValidationError
from app.domain.iam.enums import UserStatus
from app.domain.iam.exceptions import DuplicateEmailError, InvalidEmailError, RoleNotFoundError
from app.domain.iam.value_objects import Email
from tests.fakes.fake_role_repository import FakeRoleRepository


def build_use_case(
    user_repo,
    user_role_repo,
    role_repo,
    password_hasher,
    id_generator,
    clock,
    notification_service,
    uow,
) -> RegisterUserUseCase:
    return RegisterUserUseCase(
        user_repo=user_repo,
        user_role_repo=user_role_repo,
        role_repo=role_repo,
        password_hasher=password_hasher,
        id_generator=id_generator,
        clock=clock,
        notification_service=notification_service,
        uow=uow,
    )


class TestRegisterUserUseCase:
    def test_register_creates_pending_user_with_customer_role(
        self,
        user_repo,
        user_role_repo,
        role_repo,
        password_hasher,
        id_generator,
        clock,
        notification_service,
        uow,
    ):
        use_case = build_use_case(
            user_repo, user_role_repo, role_repo, password_hasher,
            id_generator, clock, notification_service, uow,
        )

        result = use_case.execute(
            RegisterUserCommand(
                email="new@example.com", password="pw", first_name="Ada", last_name="Lovelace"
            )
        )

        assert result.status == UserStatus.PENDING.value
        assert result.email == "new@example.com"
        user = user_repo.get_by_email(Email("new@example.com"))
        assert user.status == UserStatus.PENDING
        assert user_role_repo.find_active(user.id, "role-customer") is not None
        assert uow.committed is True
        assert notification_service.verification_tokens

    def test_register_duplicate_email_raises(
        self,
        user_repo,
        user_role_repo,
        role_repo,
        password_hasher,
        id_generator,
        clock,
        notification_service,
        uow,
        make_user,
    ):
        make_user(email="dup@example.com")
        use_case = build_use_case(
            user_repo, user_role_repo, role_repo, password_hasher,
            id_generator, clock, notification_service, uow,
        )

        with pytest.raises(DuplicateEmailError):
            use_case.execute(
                RegisterUserCommand(
                    email="dup@example.com", password="pw", first_name="A", last_name="B"
                )
            )

    def test_register_invalid_email_raises(
        self,
        user_repo,
        user_role_repo,
        role_repo,
        password_hasher,
        id_generator,
        clock,
        notification_service,
        uow,
    ):
        use_case = build_use_case(
            user_repo, user_role_repo, role_repo, password_hasher,
            id_generator, clock, notification_service, uow,
        )

        with pytest.raises(InvalidEmailError):
            use_case.execute(
                RegisterUserCommand(
                    email="not-an-email", password="pw", first_name="A", last_name="B"
                )
            )

    def test_register_missing_fields_raises_validation_error(
        self,
        user_repo,
        user_role_repo,
        role_repo,
        password_hasher,
        id_generator,
        clock,
        notification_service,
        uow,
    ):
        use_case = build_use_case(
            user_repo, user_role_repo, role_repo, password_hasher,
            id_generator, clock, notification_service, uow,
        )

        with pytest.raises(ValidationError):
            use_case.execute(
                RegisterUserCommand(email="", password="", first_name="", last_name="")
            )

    def test_register_missing_default_role_raises(
        self,
        user_repo,
        user_role_repo,
        password_hasher,
        id_generator,
        clock,
        notification_service,
        uow,
    ):
        use_case = build_use_case(
            user_repo, user_role_repo, FakeRoleRepository(), password_hasher,
            id_generator, clock, notification_service, uow,
        )

        with pytest.raises(RoleNotFoundError):
            use_case.execute(
                RegisterUserCommand(
                    email="new@example.com", password="pw", first_name="A", last_name="B"
                )
            )
