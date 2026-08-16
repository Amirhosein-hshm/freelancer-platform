from datetime import UTC, datetime
from decimal import Decimal

import pytest

from app.domain.category.entities import Category
from app.domain.iam.entities import User
from app.domain.iam.enums import UserStatus
from app.domain.iam.value_objects import Email, PasswordHash
from app.domain.project.entities import Project
from app.domain.project.enums import BudgetType, ProjectPriority, ProjectStatus, ProjectVisibility
from app.domain.project.value_objects import Budget, ProjectCode
from tests.fakes.fake_category_repository import FakeCategoryRepository
from tests.fakes.fake_category_supervisor_repository import FakeCategorySupervisorRepository
from tests.fakes.fake_password_hasher import FakePasswordHasher
from tests.fakes.fake_project_repository import FakeProjectRepository
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


@pytest.fixture
def project_repo() -> FakeProjectRepository:
    return FakeProjectRepository()


@pytest.fixture
def make_project(project_repo: FakeProjectRepository):
    async def _make(
        project_id: str = "proj-1",
        category_id: str = "cat-1",
        form_template_id: str = "template-1",
        status: ProjectStatus = ProjectStatus.DRAFT,
        **overrides: object,
    ) -> Project:
        project = Project(
            id=project_id,
            project_code=ProjectCode("PRJ-2026-001"),
            customer_user_id="customer-1",
            category_id=category_id,
            form_template_id=form_template_id,
            assigned_supervisor_user_id=None,
            selected_application_id=None,
            title="Test project",
            description="Description",
            visibility=ProjectVisibility.PUBLIC,
            priority=ProjectPriority.NORMAL,
            budget=Budget(
                budget_type=BudgetType.FIXED,
                fixed_amount=Decimal("100"),
                min_amount=None,
                max_amount=None,
                currency_code="USD",
            ),
            status=status,
            application_deadline=None,
            start_at=None,
            due_at=None,
            completed_at=None,
            cancelled_at=None,
            locked_at=None,
            deleted_at=None,
            created_by_user_id="customer-1",
            created_at=NOW,
            **overrides,  # type: ignore[arg-type]
        )
        await project_repo.add(project)
        return project

    return _make
