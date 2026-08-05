from datetime import datetime

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.iam.entities import RefreshToken
from app.domain.iam.exceptions import RefreshTokenNotFoundError
from app.domain.iam.repositories import IRefreshTokenRepository
from app.domain.shared.types import EntityId
from app.infrastructure.db.models.iam_models import RefreshTokenModel


def to_domain_refresh_token(row: object) -> RefreshToken:
    return RefreshToken(
        id=row.id,
        user_id=row.user_id,
        jti=row.jti,
        token_hash=row.token_hash,
        issued_at=row.issued_at,
        expires_at=row.expires_at,
        device_name=row.device_name,
        ip_address=row.ip_address,
        user_agent=row.user_agent,
        revoked_at=row.revoked_at,
        replaced_by_token_id=row.replaced_by_token_id,
        created_at=row.created_at,
    )


class SqlAlchemyRefreshTokenRepository(IRefreshTokenRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, token: RefreshToken) -> None:
        self._session.add(
            RefreshTokenModel(
                id=token.id,
                user_id=token.user_id,
                jti=token.jti,
                token_hash=token.token_hash,
                issued_at=token.issued_at,
                expires_at=token.expires_at,
                device_name=token.device_name,
                ip_address=token.ip_address,
                user_agent=token.user_agent,
                revoked_at=token.revoked_at,
                replaced_by_token_id=token.replaced_by_token_id,
                created_at=token.created_at,
            )
        )

    async def get_by_jti(self, jti: str) -> RefreshToken:
        result = await self._session.execute(
            select(RefreshTokenModel).where(RefreshTokenModel.jti == jti)
        )
        row = result.scalar_one_or_none()
        if row is None:
            raise RefreshTokenNotFoundError(f"Refresh token with jti {jti} not found.")
        return to_domain_refresh_token(row)

    async def find_by_token_hash(self, token_hash: str) -> RefreshToken | None:
        result = await self._session.execute(
            select(RefreshTokenModel).where(RefreshTokenModel.token_hash == token_hash)
        )
        row = result.scalar_one_or_none()
        return to_domain_refresh_token(row) if row is not None else None

    async def update(self, token: RefreshToken) -> None:
        row = await self._session.get(RefreshTokenModel, token.id)
        if row is None:
            raise RefreshTokenNotFoundError(f"Refresh token {token.id} not found.")
        row.revoked_at = token.revoked_at
        row.replaced_by_token_id = token.replaced_by_token_id

    async def revoke_all_for_user(self, user_id: EntityId, at: datetime) -> None:
        await self._session.execute(
            update(RefreshTokenModel)
            .where(
                RefreshTokenModel.user_id == user_id,
                RefreshTokenModel.revoked_at.is_(None),
            )
            .values(revoked_at=at)
        )