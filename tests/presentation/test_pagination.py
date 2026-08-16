"""Pagination ``meta`` shape test on a list endpoint.

Per API_DESIGN.md §2/§5 list responses carry ``meta`` with ``page``,
``page_size``, ``total_items`` and ``total_pages``.
"""

from datetime import UTC, datetime
from decimal import Decimal

from fastapi.testclient import TestClient

from app.domain.iam.entities import User
from app.domain.iam.enums import UserStatus
from app.domain.iam.value_objects import Email, PasswordHash
from app.domain.project.entities import Project
from app.domain.project.enums import BudgetType, ProjectPriority, ProjectStatus, ProjectVisibility
from app.domain.project.value_objects import Budget, ProjectCode
from app.presentation.core import providers
from tests.fakes.fake_project_repository import FakeProjectRepository
from tests.fakes.fake_user_repository import FakeUserRepository
from tests.presentation.conftest import auth_header

NOW = datetime(2026, 8, 2, tzinfo=UTC)


def _seed_user(user_repo: FakeUserRepository) -> None:
    user = User(
        id="user-1",
        created_at=NOW,
        email=Email("owner@example.com"),
        phone=None,
        password_hash=PasswordHash("fake-hash:secret"),
        first_name="Jane",
        last_name="Doe",
        status=UserStatus.ACTIVE,
    )
    user_repo._store[user.id] = user
    user_repo._by_email[user.email.value] = user


def _seed_projects(project_repo: FakeProjectRepository, count: int) -> None:
    for i in range(count):
        project_repo._store[f"proj-{i}"] = Project(
            id=f"proj-{i}",
            created_at=NOW,
            project_code=ProjectCode(f"PRJ-2026-{i + 1:03d}"),
            customer_user_id="user-1",
            category_id="cat-1",
            form_template_id="tmpl-1",
            assigned_supervisor_user_id=None,
            selected_application_id=None,
            title=f"Project {i}",
            description="desc",
            visibility=ProjectVisibility.PUBLIC,
            priority=ProjectPriority.NORMAL,
            budget=Budget(
                budget_type=BudgetType.FIXED,
                fixed_amount=Decimal("100.00"),
                min_amount=None,
                max_amount=None,
                currency_code="USD",
            ),
            status=ProjectStatus.DRAFT,
            application_deadline=None,
            start_at=None,
            due_at=None,
            completed_at=None,
            cancelled_at=None,
            locked_at=None,
            deleted_at=None,
        )


def test_list_endpoint_pagination_meta(client: TestClient, overrides) -> None:
    _seed_user(overrides[providers.get_user_repository])
    _seed_projects(overrides[providers.get_project_repository], count=5)

    headers = auth_header(None, "user-1", ["customer"])
    resp = client.get("/api/v1/projects/my?page=1&page_size=2", headers=headers)

    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert isinstance(body["data"], list)
    assert len(body["data"]) == 5
    meta = body["meta"]
    assert meta == {"page": 1, "page_size": 2, "total_items": 5, "total_pages": 3}


def test_list_endpoint_meta_defaults(client: TestClient, overrides) -> None:
    _seed_user(overrides[providers.get_user_repository])
    _seed_projects(overrides[providers.get_project_repository], count=3)

    headers = auth_header(None, "user-1", ["customer"])
    resp = client.get("/api/v1/projects/my", headers=headers)

    assert resp.status_code == 200
    meta = resp.json()["meta"]
    assert meta == {"page": 1, "page_size": 20, "total_items": 3, "total_pages": 1}
