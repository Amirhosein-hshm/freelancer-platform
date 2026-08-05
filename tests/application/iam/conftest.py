from datetime import UTC, datetime

import pytest

from app.domain.iam.entities import Role, User
from app.domain.iam.enums import UserStatus
from app.domain.iam.value_objects import Email, PasswordHash
from tests.fakes.fake_password_hasher import FakePasswordHasher
from tests.fakes.fake_permission_repository import FakePermissionRepository
from tests.fakes.fake_refresh_token_repository import FakeRefreshTokenRepository
from tests.fakes.fake_role_permission_repository import FakeRolePermissionRepository
from tests.fakes.fake_role_repository import FakeRoleRepository
from tests.fakes.fake_user_repository import FakeUserRepository
from tests.fakes.fake_user_role_repository import FakeUserRoleRepository

NOW = datetime(2026, 8, 2, tzinfo=UTC)
DEFAULT_PASSWORD = "secret"


@pytest.fixture
def user_repo() -> FakeUserRepository:
    return FakeUserRepository()


@pytest.fixture
async def role_repo() -> FakeRoleRepository:
    repo = FakeRoleRepository()
    await repo.add(
        Role(
            id="role-customer",
            role_key="customer",
            name="Customer",
            is_system=False,
            created_at=NOW,
        )
    )
    await repo.add(
        Role(id="role-admin", role_key="admin", name="Admin", is_system=False, created_at=NOW)
    )
    await repo.add(
        Role(id="role-system", role_key="system", name="System", is_system=True, created_at=NOW)
    )
    return repo


@pytest.fixture
def permission_repo() -> FakePermissionRepository:
    return FakePermissionRepository()


@pytest.fixture
def user_role_repo(role_repo: FakeRoleRepository) -> FakeUserRoleRepository:
    return FakeUserRoleRepository(role_repo)


@pytest.fixture
def role_permission_repo(
    permission_repo: FakePermissionRepository,
) -> FakeRolePermissionRepository:
    return FakeRolePermissionRepository(permission_repo)


@pytest.fixture
def refresh_token_repo() -> FakeRefreshTokenRepository:
    return FakeRefreshTokenRepository()


@pytest.fixture
def make_user(user_repo: FakeUserRepository) -> "object":
    hasher = FakePasswordHasher()

    async def _make(
        user_id: str = "user-1",
        email: str = "user@example.com",
        status: UserStatus = UserStatus.ACTIVE,
        password: str = DEFAULT_PASSWORD,
        **overrides: object,
    ) -> User:
        user = User(
            id=user_id,
            email=Email(email),
            phone=None,
            password_hash=PasswordHash(await hasher.hash(password)),
            first_name="John",
            last_name="Doe",
            status=status,
            created_at=NOW,
            **overrides,  # type: ignore[arg-type]
        )
        await user_repo.add(user)
        return user

    return _make
