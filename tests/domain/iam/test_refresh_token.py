from datetime import UTC, datetime, timedelta

from app.domain.iam.entities import RefreshToken
from app.domain.iam.value_objects import Email

NOW = datetime(2026, 8, 2, tzinfo=UTC)


def make_refresh_token(**overrides: object) -> RefreshToken:
    defaults: dict[str, object] = {
        "id": "token-1",
        "user_id": "user-1",
        "jti": "jti-1",
        "token_hash": "hash:refresh.abc",
        "issued_at": NOW,
        "expires_at": NOW + timedelta(days=30),
        "device_name": "iPhone",
        "ip_address": "127.0.0.1",
        "user_agent": "pytest",
        "created_at": NOW,
    }
    defaults.update(overrides)
    return RefreshToken(**defaults)  # type: ignore[arg-type]


class TestRefreshTokenValidity:
    def test_fresh_token_is_valid(self):
        assert make_refresh_token().is_valid(NOW) is True

    def test_revoked_token_is_invalid(self):
        token = make_refresh_token(revoked_at=NOW)
        assert token.is_valid(NOW) is False

    def test_expired_token_is_invalid(self):
        token = make_refresh_token(expires_at=NOW - timedelta(minutes=1))
        assert token.is_valid(NOW) is False


class TestRefreshTokenRevoke:
    def test_revoke_marks_revoked_at(self):
        token = make_refresh_token()
        token.revoke(NOW)
        assert token.revoked_at == NOW
        assert token.is_valid(NOW) is False

    def test_revoke_records_replaced_by(self):
        token = make_refresh_token()
        token.revoke(NOW, replaced_by="token-2")
        assert token.replaced_by_token_id == "token-2"


class TestValueObjectUsage:
    def test_email_value_object(self):
        assert Email("a@b.com").value == "a@b.com"
