from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.iam.entities import User
from app.domain.iam.enums import UserStatus
from app.domain.iam.exceptions import UserNotFoundError
from app.domain.iam.repositories import IUserRepository
from app.domain.iam.value_objects import Email
from app.domain.shared.types import EntityId
from app.infrastructure.db.models.iam_models import UserModel
from app.infrastructure.repositories.iam_mapping import to_domain_user


class SqlAlchemyUserRepository(IUserRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, user: User) -> None:
        self._session.add(
            UserModel(
                id=user.id,
                email=user.email.value,
                phone=user.phone.value if user.phone else None,
                password_hash=user.password_hash.value,
                first_name=user.first_name,
                last_name=user.last_name,
                status=user.status.value,
                created_at=user.created_at,
                email_verified_at=user.email_verified_at,
                phone_verified_at=user.phone_verified_at,
                last_login_at=user.last_login_at,
                password_changed_at=user.password_changed_at,
                deleted_at=user.deleted_at,
            )
        )

    async def get_by_id(self, user_id: EntityId) -> User:
        user = await self.find_by_id(user_id)
        if user is None:
            raise UserNotFoundError(f"User {user_id} not found.")
        return user

    async def find_by_id(self, user_id: EntityId) -> User | None:
        result = await self._session.execute(
            select(UserModel).where(UserModel.id == user_id, UserModel.deleted_at.is_(None))
        )
        row = result.scalar_one_or_none()
        return to_domain_user(row) if row is not None else None

    async def get_by_email(self, email: Email) -> User:
        result = await self._session.execute(
            select(UserModel).where(UserModel.email == email.value, UserModel.deleted_at.is_(None))
        )
        row = result.scalar_one_or_none()
        if row is None:
            raise UserNotFoundError(f"User with email {email.value} not found.")
        return to_domain_user(row)

    async def exists_by_email(self, email: Email) -> bool:
        result = await self._session.execute(
            select(UserModel.id).where(UserModel.email == email.value, UserModel.deleted_at.is_(None)).limit(1)
        )
        return result.scalar_one_or_none() is not None

    async def email_exists_including_deleted(self, email: Email) -> bool:
        result = await self._session.execute(select(UserModel.id).where(UserModel.email == email.value).limit(1))
        return result.scalar_one_or_none() is not None

    async def update(self, user: User) -> None:
        row = await self._session.get(UserModel, user.id)
        if row is None:
            raise UserNotFoundError(f"User {user.id} not found.")
        row.email = user.email.value
        row.phone = user.phone.value if user.phone else None
        row.password_hash = user.password_hash.value
        row.first_name = user.first_name
        row.last_name = user.last_name
        row.status = user.status.value
        row.email_verified_at = user.email_verified_at
        row.phone_verified_at = user.phone_verified_at
        row.last_login_at = user.last_login_at
        row.password_changed_at = user.password_changed_at
        row.deleted_at = user.deleted_at

    async def list_by_status(self, status: UserStatus, limit: int, offset: int) -> list[User]:
        result = await self._session.execute(
            select(UserModel)
            .where(UserModel.status == status.value, UserModel.deleted_at.is_(None))
            .order_by(UserModel.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return [to_domain_user(row) for row in result.scalars().all()]

    async def list_all(self, limit: int, offset: int) -> list[User]:
        result = await self._session.execute(
            select(UserModel)
            .where(UserModel.deleted_at.is_(None))
            .order_by(UserModel.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return [to_domain_user(row) for row in result.scalars().all()]

    async def count_all(self, status: UserStatus | None = None) -> int:
        stmt = select(func.count()).select_from(UserModel).where(UserModel.deleted_at.is_(None))
        if status is not None:
            stmt = stmt.where(UserModel.status == status.value)
        return int((await self._session.execute(stmt)).scalar_one())
