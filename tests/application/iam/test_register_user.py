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
    async def test_register_creates_active_customer_user(
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

        result = await use_case.execute(
            RegisterUserCommand(
                email="new@example.com",
                password="pw",
                first_name="Ada",
                last_name="Lovelace",
                role="customer",
            )
        )

        assert result.status == UserStatus.ACTIVE.value
        assert result.role == "customer"
        assert result.email == "new@example.com"
        user = await user_repo.get_by_email(Email("new@example.com"))
        assert user.status == UserStatus.ACTIVE
        assert (await user_role_repo.find_active(user.id, "role-customer")) is not None
        assert uow.committed is True
        assert notification_service.verification_tokens

    async def test_register_with_freelancer_role_assigns_freelancer_role_only(
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

        result = await use_case.execute(
            RegisterUserCommand(
                email="freelancer@example.com",
                password="pw",
                first_name="Grace",
                last_name="Hopper",
                role="freelancer",
            )
        )

        assert result.role == "freelancer"
        user = await user_repo.get_by_email(Email("freelancer@example.com"))
        assert (await user_role_repo.find_active(user.id, "role-freelancer")) is not None
        assert (await user_role_repo.find_active(user.id, "role-customer")) is None

    async def test_register_duplicate_email_raises(
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
        await make_user(email="dup@example.com")
        use_case = build_use_case(
            user_repo, user_role_repo, role_repo, password_hasher,
            id_generator, clock, notification_service, uow,
        )

        with pytest.raises(DuplicateEmailError):
            await use_case.execute(
                RegisterUserCommand(
                    email="dup@example.com",
                    password="pw",
                    first_name="A",
                    last_name="B",
                    role="customer",
                )
            )

    async def test_register_invalid_email_raises(
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
            await use_case.execute(
                RegisterUserCommand(
                    email="not-an-email",
                    password="pw",
                    first_name="A",
                    last_name="B",
                    role="customer",
                )
            )

    async def test_register_missing_fields_raises_validation_error(
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
            await use_case.execute(
                RegisterUserCommand(
                    email="", password="", first_name="", last_name="", role="customer"
                )
            )

    @pytest.mark.parametrize(
        "role",
        ["admin", "supervisor", "system", "unknown-key"],
    )
    async def test_register_disallowed_role_raises_validation_error(
        self,
        user_repo,
        user_role_repo,
        role_repo,
        password_hasher,
        id_generator,
        clock,
        notification_service,
        uow,
        role,
    ):
        use_case = build_use_case(
            user_repo, user_role_repo, role_repo, password_hasher,
            id_generator, clock, notification_service, uow,
        )

        with pytest.raises(ValidationError):
            await use_case.execute(
                RegisterUserCommand(
                    email="new@example.com",
                    password="pw",
                    first_name="A",
                    last_name="B",
                    role=role,
                )
            )

        assert await user_repo.exists_by_email(Email("new@example.com")) is False

    async def test_register_missing_seeded_role_raises(
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
            await use_case.execute(
                RegisterUserCommand(
                    email="new@example.com",
                    password="pw",
                    first_name="A",
                    last_name="B",
                    role="customer",
                )
            )