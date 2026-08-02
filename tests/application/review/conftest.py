from datetime import UTC, datetime
from decimal import Decimal

import pytest

from app.domain.category.entities import Category, CategorySupervisor
from app.domain.project.entities import Project, ProjectDelivery
from app.domain.project.enums import (
    BudgetType,
    DeliveryStatus,
    ProjectPriority,
    ProjectStatus,
    ProjectVisibility,
)
from app.domain.project.value_objects import Budget, ProjectCode
from app.domain.review.entities import SupervisorReview
from app.domain.review.enums import ReviewStatus
from tests.fakes.fake_category_repository import FakeCategoryRepository
from tests.fakes.fake_category_supervisor_repository import FakeCategorySupervisorRepository
from tests.fakes.fake_project_delivery_repository import FakeProjectDeliveryRepository
from tests.fakes.fake_project_repository import FakeProjectRepository
from tests.fakes.fake_project_revision_request_repository import FakeProjectRevisionRequestRepository
from tests.fakes.fake_project_status_history_repository import FakeProjectStatusHistoryRepository
from tests.fakes.fake_supervisor_review_repository import FakeSupervisorReviewRepository

NOW = datetime(2026, 8, 2, tzinfo=UTC)


@pytest.fixture
def project_repo() -> FakeProjectRepository:
    return FakeProjectRepository()


@pytest.fixture
def category_repo() -> FakeCategoryRepository:
    return FakeCategoryRepository()


@pytest.fixture
def category_supervisor_repo() -> FakeCategorySupervisorRepository:
    return FakeCategorySupervisorRepository()


@pytest.fixture
def delivery_repo() -> FakeProjectDeliveryRepository:
    return FakeProjectDeliveryRepository()


@pytest.fixture
def review_repo() -> FakeSupervisorReviewRepository:
    return FakeSupervisorReviewRepository()


@pytest.fixture
def revision_repo() -> FakeProjectRevisionRequestRepository:
    return FakeProjectRevisionRequestRepository()


@pytest.fixture
def status_history_repo() -> FakeProjectStatusHistoryRepository:
    return FakeProjectStatusHistoryRepository()


@pytest.fixture
def seed_supervisor_flow(
    category_repo,
    category_supervisor_repo,
    project_repo,
    delivery_repo,
    review_repo,
):
    def _seed(
        supervisor_user_id: str = "supervisor-1",
        project_id: str = "project-1",
        delivery_id: str = "delivery-1",
        category_id: str = "cat-1",
        with_review: bool = True,
    ) -> ProjectDelivery:
        category_repo.add(
            Category(
                id=category_id,
                parent_category_id=None,
                category_key="webdev",
                name="Web Development",
                slug="web-development",
                description=None,
                is_active=True,
                sort_order=0,
                created_at=NOW,
            )
        )
        category_supervisor_repo.add(
            CategorySupervisor(
                id=f"{category_id}-supervisor-{supervisor_user_id}",
                category_id=category_id,
                supervisor_user_id=supervisor_user_id,
                assigned_by_user_id="admin-1",
                is_primary=True,
                is_active=True,
                assigned_at=NOW,
                created_at=NOW,
            )
        )
        project_repo.add(
            Project(
                id=project_id,
                project_code=ProjectCode("PRJ-2026-001"),
                customer_user_id="customer-1",
                category_id=category_id,
                form_template_id="template-1",
                assigned_supervisor_user_id=supervisor_user_id,
                selected_application_id="app-1",
                title="Build an API",
                description="REST API for orders",
                visibility=ProjectVisibility.PUBLIC,
                priority=ProjectPriority.NORMAL,
                budget=Budget(
                    budget_type=BudgetType.FIXED,
                    fixed_amount=Decimal("1000"),
                    min_amount=None,
                    max_amount=None,
                    currency_code="USD",
                ),
                status=ProjectStatus.UNDER_SUPERVISOR_REVIEW,
                application_deadline=None,
                start_at=None,
                due_at=None,
                completed_at=None,
                cancelled_at=None,
                locked_at=None,
                deleted_at=None,
                created_at=NOW,
            )
        )
        delivery = ProjectDelivery(
            id=delivery_id,
            project_id=project_id,
            version_no=1,
            submitted_by_user_id="freelancer-1",
            status=DeliveryStatus.UNDER_REVIEW,
            delivery_note="v1",
            submitted_at=NOW,
            reviewed_at=None,
            reviewer_user_id=None,
            superseded_by_delivery_id=None,
            file_asset_ids=[],
            created_at=NOW,
        )
        delivery_repo.add(delivery)
        if with_review:
            review_repo.add(
                SupervisorReview(
                    id=f"review-{delivery_id}",
                    project_delivery_id=delivery_id,
                    project_id=project_id,
                    supervisor_user_id=supervisor_user_id,
                    decision=ReviewStatus.PENDING,
                    reject_reason=None,
                    notes=None,
                    reviewed_at=None,
                    created_at=NOW,
                )
            )
        return delivery

    return _seed
