from datetime import datetime

from app.domain.iam.entities import RefreshToken
from app.domain.iam.exceptions import RefreshTokenNotFoundError
from app.domain.iam.repositories import IRefreshTokenRepository
from app.domain.shared.types import EntityId


class FakeRefreshTokenRepository(IRefreshTokenRepository):
    def __init__(self) -> None:
        self._store: dict[str, RefreshToken] = {}
        self._by_hash: dict[str, RefreshToken] = {}

    def add(self, token: RefreshToken) -> None:
        self._store[token.jti] = token
        self._by_hash[token.token_hash] = token

    def get_by_jti(self, jti: str) -> RefreshToken:
        try:
            return self._store[jti]
        except KeyError:
            raise RefreshTokenNotFoundError(f"Refresh token {jti} not found.") from None

    def find_by_token_hash(self, token_hash: str) -> RefreshToken | None:
        return self._by_hash.get(token_hash)

    def update(self, token: RefreshToken) -> None:
        self._store[token.jti] = token
        self._by_hash[token.token_hash] = token

    def revoke_all_for_user(self, user_id: EntityId, at: datetime) -> None:
        for token in self._store.values():
            if token.user_id == user_id:
                token.revoke(at)
