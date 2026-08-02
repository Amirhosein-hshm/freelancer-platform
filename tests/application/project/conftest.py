from datetime import UTC, datetime
from decimal import Decimal

import pytest

from app.domain.category.entities import Category
from app.domain.freelancer.entities import FreelancerLevel, FreelancerProfile
from app.domain.freelancer.enums import (
    FreelancerApprovalStatus,
    FreelancerLevelAccessType,
)
from app.domain.project.entities import Project
from app.domain.project.enums import (
    BudgetType,
    ProjectPriority,
    ProjectStatus,
    ProjectVisibility,
)
from app.domain.project.value_objects import Budget, ProjectCode
from tests.fakes.fake_category_repository import FakeCategoryRepository
from tests.fakes.fake_form_template_repository import FakeFormTemplateRepository
from tests.fakes.fake_freelancer_level_repository import FakeFreelancerLevelRepository
from tests.fakes.fake_freelancer_profile_repository import FakeFreelancerProfileRepository
from tests.fakes.fake_project_application_repository import FakeProjectApplicationRepository
from tests.fakes.fake_project_delivery_repository import FakeProjectDeliveryRepository
from tests.fakes.fake_project_repository import FakeProjectRepository
from tests.fakes.fake_project_revision_request_repository import FakeProjectRevisionRequestRepository
from tests.fakes.fake_project_status_history_repository import FakeProjectStatusHistoryRepository
from tests.fakes.fake_supervisor_review_repository import FakeSupervisorReviewRepository

NOW = datetime(2026, 8, 2, tzinfo=UTC)


@pytest.fixture
def category_repo() -> FakeCategoryRepository:
    return FakeCategoryRepository()


@pytest.fixture
def make_category(category_repo: FakeCategoryRepository):
    def _make(category_id: str = "cat-1", **overrides: object) -> Category:
        fields: dict[str, object] = {
            "id": category_id,
            "parent_category_id": None,
            "category_key": "webdev",
            "name": "Web Development",
            "slug": "web-development",
            "description": None,
            "is_active": True,
            "sort_order": 0,
            "created_at": NOW,
        }
        fields.update(overrides)
        category = Category(**fields)  # type: ignore[arg-type]
        category_repo.add(category)
        return category

    return _make


@pytest.fixture
def project_repo() -> FakeProjectRepository:
    return FakeProjectRepository()


@pytest.fixture
def form_template_repo() -> FakeFormTemplateRepository:
    return FakeFormTemplateRepository()


@pytest.fixture
def profile_repo() -> FakeFreelancerProfileRepository:
    return FakeFreelancerProfileRepository()


@pytest.fixture
def level_repo() -> FakeFreelancerLevelRepository:
    return FakeFreelancerLevelRepository()


@pytest.fixture
def make_level(level_repo: FakeFreelancerLevelRepository):
    def _make(level_id: str = "level-1", level_key: str = "standard", **overrides: object) -> FreelancerLevel:
        fields: dict[str, object] = {
            "id": level_id,
            "level_key": level_key,
            "name": "Standard",
            "rank_order": 1,
            "access_type": FreelancerLevelAccessType.STANDARD,
            "min_completed_projects": 0,
            "min_rating": None,
            "max_active_applications": 3,
            "can_apply_public_projects": True,
            "can_apply_private_projects": False,
            "is_active": True,
            "created_at": NOW,
        }
        fields.update(overrides)
        level = FreelancerLevel(**fields)  # type: ignore[arg-type]
        level_repo.add(level)
        return level

    return _make


@pytest.fixture
def make_profile(profile_repo: FakeFreelancerProfileRepository):
    def _make(profile_id: str = "profile-1", user_id: str = "freelancer-1", **overrides: object) -> FreelancerProfile:
        fields: dict[str, object] = {
            "id": profile_id,
            "user_id": user_id,
            "current_level_id": "level-1",
            "approval_status": FreelancerApprovalStatus.APPROVED,
            "approved_by_user_id": "admin-1",
            "approved_at": NOW,
            "approval_note": None,
            "display_name": "Jane Dev",
            "headline": None,
            "bio": None,
            "country_code": None,
            "city": None,
            "timezone": None,
            "hourly_rate_min": None,
            "hourly_rate_max": None,
            "is_available": True,
            "deleted_at": None,
            "created_at": NOW,
        }
        fields.update(overrides)
        profile = FreelancerProfile(**fields)  # type: ignore[arg-type]
        profile_repo.add(profile)
        return profile

    return _make


@pytest.fixture
def application_repo() -> FakeProjectApplicationRepository:
    return FakeProjectApplicationRepository()


@pytest.fixture
def delivery_repo() -> FakeProjectDeliveryRepository:
    return FakeProjectDeliveryRepository()


@pytest.fixture
def revision_repo() -> FakeProjectRevisionRequestRepository:
    return FakeProjectRevisionRequestRepository()


@pytest.fixture
def status_history_repo() -> FakeProjectStatusHistoryRepository:
    return FakeProjectStatusHistoryRepository()


@pytest.fixture
def review_repo() -> FakeSupervisorReviewRepository:
    return FakeSupervisorReviewRepository()


@pytest.fixture
def make_project(project_repo: FakeProjectRepository):
    def _make(
        project_id: str = "project-1",
        customer_user_id: str = "customer-1",
        status: ProjectStatus = ProjectStatus.DRAFT,
        **overrides: object,
    ) -> Project:
        fields: dict[str, object] = {
            "id": project_id,
            "project_code": ProjectCode("PRJ-2026-001"),
            "customer_user_id": customer_user_id,
            "category_id": "cat-1",
            "form_template_id": "template-1",
            "assigned_supervisor_user_id": "supervisor-1",
            "selected_application_id": None,
            "title": "Build an API",
            "description": "REST API for orders",
            "visibility": ProjectVisibility.PUBLIC,
            "priority": ProjectPriority.NORMAL,
            "budget": Budget(
                budget_type=BudgetType.FIXED,
                fixed_amount=Decimal("1000"),
                min_amount=None,
                max_amount=None,
                currency_code="USD",
            ),
            "status": status,
            "application_deadline": None,
            "start_at": None,
            "due_at": None,
            "completed_at": None,
            "cancelled_at": None,
            "locked_at": None,
            "deleted_at": None,
            "created_at": NOW,
        }
        fields.update(overrides)
        project = Project(**fields)  # type: ignore[arg-type]
        project_repo.add(project)
        return project

    return _make
