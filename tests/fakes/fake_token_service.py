from datetime import UTC, datetime, timedelta

from app.application.shared.ports import AccessTokenPayload, ITokenService
from app.domain.shared.types import EntityId


class FakeTokenService(ITokenService):
    def __init__(self) -> None:
        self._jti_counter = 0

    def generate_access_token(self, user_id: EntityId, roles: list[str]) -> str:
        roles_part = ",".join(roles)
        return f"access.{user_id}.{roles_part}"

    def generate_refresh_token(self) -> tuple[str, str]:
        self._jti_counter += 1
        jti = f"jti-{self._jti_counter}"
        return f"refresh.{jti}", jti

    def hash_refresh_token(self, raw_token: str) -> str:
        return f"hash:{raw_token}"

    def decode_access_token(self, token: str) -> AccessTokenPayload:
        _prefix, user_id, roles_part = token.split(".")
        roles = roles_part.split(",") if roles_part else []
        return AccessTokenPayload(
            user_id=user_id,
            roles=roles,
            expires_at=datetime.now(UTC) + timedelta(hours=1),
        )
