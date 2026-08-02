from datetime import UTC, datetime, timedelta

import pytest

from app.application.iam.dto import RefreshTokenCommand
from app.application.iam.use_cases.refresh_token import RefreshTokenUseCase
from app.domain.iam.entities import RefreshToken
from app.domain.iam.enums import UserStatus
from app.domain.iam.exceptions import (
    InvalidRefreshTokenError,
    UserNotActiveError,
    UserNotFoundError,
)

NOW = datetime(2026, 8, 2, tzinfo=UTC)


def build_use_case(
    refresh_token_repo,
    user_repo,
    user_role_repo,
    token_service,
    id_generator,
    clock,
    uow,
) -> RefreshTokenUseCase:
    return RefreshTokenUseCase(
        refresh_token_repo=refresh_token_repo,
        user_repo=user_repo,
        user_role_repo=user_role_repo,
        token_service=token_service,
        id_generator=id_generator,
        clock=clock,
        uow=uow,
    )


def make_token(token_service, refresh_token_repo, user_id="user-1", **overrides) -> tuple[str, RefreshToken]:
    raw, jti = token_service.generate_refresh_token()
    fields: dict[str, object] = {
        "id": "token-1",
        "user_id": user_id,
        "jti": jti,
        "token_hash": token_service.hash_refresh_token(raw),
        "issued_at": NOW,
        "expires_at": NOW + timedelta(days=30),
        "created_at": NOW,
    }
    fields.update(overrides)
    token = RefreshToken(**fields)  # type: ignore[arg-type]
    refresh_token_repo.add(token)
    return raw, token


class TestRefreshTokenUseCase:
    def test_refresh_rotates_token_and_returns_new_access_token(
        self,
        refresh_token_repo,
        user_repo,
        user_role_repo,
        token_service,
        id_generator,
        clock,
        uow,
        make_user,
    ):
        make_user(user_id="user-1")
        raw, token = make_token(token_service, refresh_token_repo)
        use_case = build_use_case(
            refresh_token_repo, user_repo, user_role_repo, token_service,
            id_generator, clock, uow,
        )

        result = use_case.execute(RefreshTokenCommand(raw_refresh_token=raw))

        assert result.access_token
        assert result.refresh_token != raw
        old = refresh_token_repo.get_by_jti(token.jti)
        assert old.revoked_at == NOW
        assert old.replaced_by_token_id is not None
        assert refresh_token_repo.get_by_jti(result.refresh_token_jti) is not None

    def test_refresh_unknown_token_raises(
        self,
        refresh_token_repo,
        user_repo,
        user_role_repo,
        token_service,
        id_generator,
        clock,
        uow,
    ):
        use_case = build_use_case(
            refresh_token_repo, user_repo, user_role_repo, token_service,
            id_generator, clock, uow,
        )

        with pytest.raises(InvalidRefreshTokenError):
            use_case.execute(RefreshTokenCommand(raw_refresh_token="garbage"))

    def test_refresh_revoked_token_raises(
        self,
        refresh_token_repo,
        user_repo,
        user_role_repo,
        token_service,
        id_generator,
        clock,
        uow,
        make_user,
    ):
        make_user(user_id="user-1")
        raw, token = make_token(token_service, refresh_token_repo, revoked_at=NOW)
        use_case = build_use_case(
            refresh_token_repo, user_repo, user_role_repo, token_service,
            id_generator, clock, uow,
        )

        with pytest.raises(InvalidRefreshTokenError):
            use_case.execute(RefreshTokenCommand(raw_refresh_token=raw))

    def test_refresh_expired_token_raises(
        self,
        refresh_token_repo,
        user_repo,
        user_role_repo,
        token_service,
        id_generator,
        clock,
        uow,
        make_user,
    ):
        make_user(user_id="user-1")
        raw, _ = make_token(
            token_service, refresh_token_repo, expires_at=NOW - timedelta(minutes=1)
        )
        use_case = build_use_case(
            refresh_token_repo, user_repo, user_role_repo, token_service,
            id_generator, clock, uow,
        )

        with pytest.raises(InvalidRefreshTokenError):
            use_case.execute(RefreshTokenCommand(raw_refresh_token=raw))

    def test_refresh_inactive_user_raises(
        self,
        refresh_token_repo,
        user_repo,
        user_role_repo,
        token_service,
        id_generator,
        clock,
        uow,
        make_user,
    ):
        make_user(user_id="user-1", status=UserStatus.PENDING)
        raw, _ = make_token(token_service, refresh_token_repo)
        use_case = build_use_case(
            refresh_token_repo, user_repo, user_role_repo, token_service,
            id_generator, clock, uow,
        )

        with pytest.raises(UserNotActiveError):
            use_case.execute(RefreshTokenCommand(raw_refresh_token=raw))

    def test_refresh_missing_user_raises(
        self,
        refresh_token_repo,
        user_repo,
        user_role_repo,
        token_service,
        id_generator,
        clock,
        uow,
    ):
        raw, _ = make_token(token_service, refresh_token_repo, user_id="ghost-user")
        use_case = build_use_case(
            refresh_token_repo, user_repo, user_role_repo, token_service,
            id_generator, clock, uow,
        )

        with pytest.raises(UserNotFoundError):
            use_case.execute(RefreshTokenCommand(raw_refresh_token=raw))
