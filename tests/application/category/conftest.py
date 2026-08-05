from datetime import UTC, datetime

import pytest

from app.domain.category.entities import Category
from app.domain.iam.entities import User
from app.domain.iam.enums import UserStatus
from app.domain.iam.value_objects import Email, PasswordHash
from tests.fakes.fake_category_repository import FakeCategoryRepository
from tests.fakes.fake_category_supervisor_repository import FakeCategorySupervisorRepository
from tests.fakes.fake_password_hasher import FakePasswordHasher
from tests.fakes.fake_user_repository import FakeUserRepository

NOW = datetime(2026, 8, 2, tzinfo=UTC)


@pytest.fixture
def user_repo() -> FakeUserRepository:
    return FakeUserRepository()


@pytest.fixture
def make_user(user_repo: FakeUserRepository):
    hasher = FakePasswordHasher()

    async def _make(
        user_id: str = "sup-1",
        email: str = "supervisor@example.com",
        status: UserStatus = UserStatus.ACTIVE,
        **overrides: object,
    ) -> User:
        user = User(
            id=user_id,
            email=Email(email),
            phone=None,
            password_hash=PasswordHash(await hasher.hash("secret")),
            first_name="Jane",
            last_name="Supervisor",
            status=status,
            created_at=NOW,
            **overrides,  # type: ignore[arg-type]
        )
        await user_repo.add(user)
        return user

    return _make


@pytest.fixture
def category_repo() -> FakeCategoryRepository:
    return FakeCategoryRepository()


@pytest.fixture
def category_supervisor_repo() -> FakeCategorySupervisorRepository:
    return FakeCategorySupervisorRepository()


@pytest.fixture
def make_category(category_repo: FakeCategoryRepository):
    async def _make(category_id: str = "cat-1", slug: str = "web-development", **overrides: object) -> Category:
        fields: dict[str, object] = {
            "id": category_id,
            "parent_category_id": None,
            "category_key": "webdev",
            "name": "Web Development",
            "slug": slug,
            "description": None,
            "is_active": True,
            "sort_order": 0,
            "created_at": NOW,
        }
        fields.update(overrides)
        category = Category(**fields)  # type: ignore[arg-type]
        await category_repo.add(category)
        return category

    return _make
