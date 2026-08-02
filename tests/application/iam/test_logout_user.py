from datetime import UTC, datetime, timedelta

import pytest

from app.application.iam.dto import LogoutUserCommand
from app.application.iam.use_cases.logout_user import LogoutUserUseCase
from app.domain.iam.entities import RefreshToken
from app.domain.iam.exceptions import RefreshTokenNotFoundError

NOW = datetime(2026, 8, 2, tzinfo=UTC)


def make_refresh_token(refresh_token_repo, jti: str = "jti-1") -> RefreshToken:
    token = RefreshToken(
        id="token-1",
        user_id="user-1",
        jti=jti,
        token_hash=f"hash:{jti}",
        issued_at=NOW,
        expires_at=NOW + timedelta(days=30),
        created_at=NOW,
    )
    refresh_token_repo.add(token)
    return token


def build_use_case(refresh_token_repo, clock, uow) -> LogoutUserUseCase:
    return LogoutUserUseCase(refresh_token_repo=refresh_token_repo, clock=clock, uow=uow)


class TestLogoutUserUseCase:
    def test_logout_revokes_token(self, refresh_token_repo, clock, uow):
        token = make_refresh_token(refresh_token_repo)
        use_case = build_use_case(refresh_token_repo, clock, uow)

        result = use_case.execute(LogoutUserCommand(refresh_token_jti=token.jti))

        assert result.user_id == token.user_id
        assert refresh_token_repo.get_by_jti(token.jti).revoked_at == NOW
        assert uow.committed is True

    def test_logout_unknown_jti_raises(self, refresh_token_repo, clock, uow):
        use_case = build_use_case(refresh_token_repo, clock, uow)

        with pytest.raises(RefreshTokenNotFoundError):
            use_case.execute(LogoutUserCommand(refresh_token_jti="missing-jti"))
