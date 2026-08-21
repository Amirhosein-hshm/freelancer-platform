from app.domain.iam.entities import User
from app.domain.iam.enums import UserStatus
from app.domain.iam.exceptions import UserNotFoundError
from app.domain.iam.repositories import IUserRepository
from app.domain.iam.value_objects import Email
from app.domain.shared.types import EntityId


class FakeUserRepository(IUserRepository):
    """Mirrors the SQLAlchemy repository: every read excludes soft-deleted users,
    except ``email_exists_including_deleted`` which models the DB UNIQUE constraint."""

    def __init__(self) -> None:
        self._store: dict[str, User] = {}
        self._by_email: dict[str, User] = {}

    async def add(self, user: User) -> None:
        self._store[user.id] = user
        self._by_email[user.email.value] = user

    async def get_by_id(self, user_id: EntityId) -> User:
        user = await self.find_by_id(user_id)
        if user is None:
            raise UserNotFoundError(f"User {user_id} not found.")
        return user

    async def find_by_id(self, user_id: EntityId) -> User | None:
        user = self._store.get(user_id)
        return None if user is None or user.deleted_at is not None else user

    async def get_by_email(self, email: Email) -> User:
        user = self._by_email.get(email.value)
        if user is None or user.deleted_at is not None:
            raise UserNotFoundError(f"User with email {email.value} not found.")
        return user

    async def exists_by_email(self, email: Email) -> bool:
        user = self._by_email.get(email.value)
        return user is not None and user.deleted_at is None

    async def email_exists_including_deleted(self, email: Email) -> bool:
        return email.value in self._by_email

    async def update(self, user: User) -> None:
        self._store[user.id] = user
        self._by_email[user.email.value] = user

    async def list_by_status(self, status: UserStatus, limit: int, offset: int) -> list[User]:
        matches = [u for u in self._store.values() if u.status == status and u.deleted_at is None]
        return matches[offset : offset + limit]

    async def list_all(self, limit: int, offset: int) -> list[User]:
        matches = [u for u in self._store.values() if u.deleted_at is None]
        return matches[offset : offset + limit]

    async def count_all(self, status: UserStatus | None = None) -> int:
        live = [u for u in self._store.values() if u.deleted_at is None]
        if status is None:
            return len(live)
        return sum(1 for u in live if u.status == status)
