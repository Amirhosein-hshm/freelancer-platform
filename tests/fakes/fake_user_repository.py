from app.domain.iam.entities import User
from app.domain.iam.enums import UserStatus
from app.domain.iam.exceptions import UserNotFoundError
from app.domain.iam.repositories import IUserRepository
from app.domain.iam.value_objects import Email
from app.domain.shared.types import EntityId


class FakeUserRepository(IUserRepository):
    def __init__(self) -> None:
        self._store: dict[str, User] = {}
        self._by_email: dict[str, User] = {}

    async def add(self, user: User) -> None:
        self._store[user.id] = user
        self._by_email[user.email.value] = user

    async def get_by_id(self, user_id: EntityId) -> User:
        try:
            return self._store[user_id]
        except KeyError:
            raise UserNotFoundError(f"User {user_id} not found.") from None

    async def find_by_id(self, user_id: EntityId) -> User | None:
        return self._store.get(user_id)

    async def get_by_email(self, email: Email) -> User:
        try:
            return self._by_email[email.value]
        except KeyError:
            raise UserNotFoundError(f"User with email {email.value} not found.") from None

    async def exists_by_email(self, email: Email) -> bool:
        return email.value in self._by_email

    async def update(self, user: User) -> None:
        self._store[user.id] = user
        self._by_email[user.email.value] = user

    async def list_by_status(self, status: UserStatus, limit: int, offset: int) -> list[User]:
        matches = [u for u in self._store.values() if u.status == status]
        return matches[offset : offset + limit]
