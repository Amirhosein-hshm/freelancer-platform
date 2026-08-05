from datetime import UTC, datetime

import pytest

from app.application.iam.dto import LoginUserCommand
from app.application.iam.use_cases.login_user import LoginUserUseCase
from app.application.shared.exceptions import ValidationError
from app.domain.iam.entities import UserRole
from app.domain.iam.enums import UserStatus
from app.domain.iam.exceptions import InvalidCredentialsError, UserNotActiveError

NOW = datetime(2026, 8, 2, tzinfo=UTC)


def build_use_case(
    user_repo,
    user_role_repo,
    refresh_token_repo,
    password_hasher,
    token_service,
    id_generator,
    clock,
    uow,
) -> LoginUserUseCase:
    return LoginUserUseCase(
        user_repo=user_repo,
        user_role_repo=user_role_repo,
        refresh_token_repo=refresh_token_repo,
        password_hasher=password_hasher,
        token_service=token_service,
        id_generator=id_generator,
        clock=clock,
        uow=uow,
    )


class TestLoginUserUseCase:
    async def test_login_success_issues_tokens_and_records_login(
        self,
        user_repo,
        user_role_repo,
        refresh_token_repo,
        password_hasher,
        token_service,
        id_generator,
        clock,
        uow,
        make_user,
    ):
        user = await make_user(user_id="u1", email="a@b.com")
        await user_role_repo.add(
            UserRole(
                id="ur-1",
                user_id=user.id,
                role_id="role-customer",
                assigned_by_user_id="admin",
                assigned_at=NOW,
                created_at=NOW,
            )
        )
        use_case = build_use_case(
            user_repo, user_role_repo, refresh_token_repo, password_hasher,
            token_service, id_generator, clock, uow,
        )

        result = await use_case.execute(LoginUserCommand(email="a@b.com", password="secret"))

        assert result.user_id == user.id
        assert "customer" in result.access_token
        assert result.refresh_token_jti
        stored = await refresh_token_repo.get_by_jti(result.refresh_token_jti)
        assert stored.user_id == user.id
        assert (await user_repo.get_by_id(user.id)).last_login_at == NOW

    async def test_login_wrong_email_raises_invalid_credentials(
        self,
        user_repo,
        user_role_repo,
        refresh_token_repo,
        password_hasher,
        token_service,
        id_generator,
        clock,
        uow,
        make_user,
    ):
        await make_user(email="a@b.com")
        use_case = build_use_case(
            user_repo, user_role_repo, refresh_token_repo, password_hasher,
            token_service, id_generator, clock, uow,
        )

        with pytest.raises(InvalidCredentialsError):
            await use_case.execute(LoginUserCommand(email="missing@b.com", password="secret"))

    async def test_login_wrong_password_raises_invalid_credentials(
        self,
        user_repo,
        user_role_repo,
        refresh_token_repo,
        password_hasher,
        token_service,
        id_generator,
        clock,
        uow,
        make_user,
    ):
        await make_user(email="a@b.com", password="correct")
        use_case = build_use_case(
            user_repo, user_role_repo, refresh_token_repo, password_hasher,
            token_service, id_generator, clock, uow,
        )

        with pytest.raises(InvalidCredentialsError):
            await use_case.execute(LoginUserCommand(email="a@b.com", password="wrong"))

    async def test_login_inactive_user_raises_not_active(
        self,
        user_repo,
        user_role_repo,
        refresh_token_repo,
        password_hasher,
        token_service,
        id_generator,
        clock,
        uow,
        make_user,
    ):
        await make_user(email="a@b.com", status=UserStatus.PENDING)
        use_case = build_use_case(
            user_repo, user_role_repo, refresh_token_repo, password_hasher,
            token_service, id_generator, clock, uow,
        )

        with pytest.raises(UserNotActiveError):
            await use_case.execute(LoginUserCommand(email="a@b.com", password="secret"))

    async def test_login_missing_fields_raises_validation_error(
        self,
        user_repo,
        user_role_repo,
        refresh_token_repo,
        password_hasher,
        token_service,
        id_generator,
        clock,
        uow,
    ):
        use_case = build_use_case(
            user_repo, user_role_repo, refresh_token_repo, password_hasher,
            token_service, id_generator, clock, uow,
        )

        with pytest.raises(ValidationError):
            await use_case.execute(LoginUserCommand(email="", password=""))
