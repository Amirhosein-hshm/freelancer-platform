from datetime import UTC, datetime, timedelta

import pytest

from app.application.iam.dto import LogoutUserCommand
from app.application.iam.use_cases.logout_user import LogoutUserUseCase
from app.domain.iam.entities import RefreshToken
from app.domain.iam.exceptions import InvalidRefreshTokenError

NOW = datetime(2026, 8, 2, tzinfo=UTC)


async def make_refresh_token(refresh_token_repo, jti: str = "jti-1") -> RefreshToken:
    token = RefreshToken(
        id="token-1",
        user_id="user-1",
        jti=jti,
        token_hash=f"hash:refresh.{jti}",
        issued_at=NOW,
        expires_at=NOW + timedelta(days=30),
        created_at=NOW,
    )
    await refresh_token_repo.add(token)
    return token


def build_use_case(refresh_token_repo, token_service, clock, uow) -> LogoutUserUseCase:
    return LogoutUserUseCase(refresh_token_repo, token_service, clock, uow)


class TestLogoutUserUseCase:
    async def test_logout_revokes_token(self, refresh_token_repo, token_service, clock, uow):
        token = await make_refresh_token(refresh_token_repo)
        use_case = build_use_case(refresh_token_repo, token_service, clock, uow)

        result = await use_case.execute(LogoutUserCommand(raw_refresh_token=f"refresh.{token.jti}"))

        assert result.user_id == token.user_id
        assert (await refresh_token_repo.get_by_jti(token.jti)).revoked_at == NOW
        assert uow.committed is True

    async def test_logout_unknown_token_raises(self, refresh_token_repo, token_service, clock, uow):
        use_case = build_use_case(refresh_token_repo, token_service, clock, uow)

        with pytest.raises(InvalidRefreshTokenError):
            await use_case.execute(LogoutUserCommand(raw_refresh_token="missing-token"))
