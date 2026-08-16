import hashlib
import secrets
from datetime import UTC, datetime, timedelta

import jwt

from app.application.shared.exceptions import ExpiredTokenError, InvalidTokenError
from app.application.shared.ports import AccessTokenPayload, ITokenService
from app.domain.shared.types import EntityId


class JwtTokenService(ITokenService):
    """Access tokens via PyJWT (HS256); refresh tokens are opaque, revocable strings."""

    def __init__(self, secret: str, access_ttl_minutes: int, refresh_ttl_days: int) -> None:
        self._secret = secret
        self._access_ttl = timedelta(minutes=access_ttl_minutes)
        self._refresh_ttl = timedelta(days=refresh_ttl_days)

    async def generate_access_token(self, user_id: EntityId, roles: list[str]) -> str:
        now = datetime.now(UTC)
        payload = {
            "sub": user_id,
            "roles": roles,
            "iat": int(now.timestamp()),
            "exp": int((now + self._access_ttl).timestamp()),
        }
        return jwt.encode(payload, self._secret, algorithm="HS256")

    async def generate_refresh_token(self) -> tuple[str, str]:
        raw = secrets.token_urlsafe(32)
        jti = secrets.token_urlsafe(16)
        return raw, jti

    async def hash_refresh_token(self, raw_token: str) -> str:
        return hashlib.sha256(raw_token.encode()).hexdigest()

    async def decode_access_token(self, token: str) -> AccessTokenPayload:
        try:
            payload = jwt.decode(token, self._secret, algorithms=["HS256"])
        except jwt.ExpiredSignatureError as exc:
            raise ExpiredTokenError("Access token has expired.") from exc
        except jwt.PyJWTError as exc:
            raise InvalidTokenError("Access token is invalid.") from exc
        return AccessTokenPayload(
            user_id=payload["sub"],
            roles=list(payload.get("roles", [])),
            expires_at=datetime.fromtimestamp(payload["exp"], tz=UTC),
        )
