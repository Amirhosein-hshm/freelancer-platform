from datetime import UTC, datetime
from decimal import Decimal

import pytest

from app.domain.feedback.entities import CustomerReview, Rating
from app.domain.project.entities import Project, ProjectApplication, ProjectDelivery
from app.domain.project.enums import (
    BudgetType,
    DeliveryStatus,
    ProjectApplicationStatus,
    ProjectPriority,
    ProjectStatus,
    ProjectVisibility,
)
from app.domain.project.value_objects import Budget, ProjectCode
from app.domain.review.enums import ReviewStatus
from tests.fakes.fake_customer_review_repository import FakeCustomerReviewRepository
from tests.fakes.fake_project_application_repository import FakeProjectApplicationRepository
from tests.fakes.fake_project_delivery_repository import FakeProjectDeliveryRepository
from tests.fakes.fake_project_repository import FakeProjectRepository
from tests.fakes.fake_project_revision_request_repository import FakeProjectRevisionRequestRepository
from tests.fakes.fake_project_status_history_repository import FakeProjectStatusHistoryRepository
from tests.fakes.fake_rating_repository import FakeRatingRepository

NOW = datetime(2026, 8, 2, tzinfo=UTC)


@pytest.fixture
def project_repo() -> FakeProjectRepository:
    return FakeProjectRepository()


@pytest.fixture
def application_repo() -> FakeProjectApplicationRepository:
    return FakeProjectApplicationRepository()


@pytest.fixture
def customer_review_repo() -> FakeCustomerReviewRepository:
    return FakeCustomerReviewRepository()


@pytest.fixture
def rating_repo() -> FakeRatingRepository:
    return FakeRatingRepository()


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
def make_project(project_repo: FakeProjectRepository):
    async def _make(
        project_id: str = "project-1",
        status: ProjectStatus = ProjectStatus.AWAITING_CUSTOMER_REVIEW,
        **overrides: object,
    ) -> Project:
        fields: dict[str, object] = {
            "id": project_id,
            "project_code": ProjectCode("PRJ-2026-001"),
            "customer_user_id": "customer-1",
            "category_id": "cat-1",
            "form_template_id": "template-1",
            "assigned_supervisor_user_id": None,
            "selected_application_id": "app-1",
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
        await project_repo.add(project)
        return project

    return _make


@pytest.fixture
def make_application(application_repo: FakeProjectApplicationRepository):
    async def _make(app_id: str = "app-1", profile_id: str = "profile-1", **overrides: object) -> ProjectApplication:
        fields: dict[str, object] = {
            "id": app_id,
            "project_id": "project-1",
            "freelancer_profile_id": profile_id,
            "status": ProjectApplicationStatus.ACCEPTED,
            "cover_letter": None,
            "proposed_amount": Decimal("800"),
            "proposed_days": 10,
            "applied_at": NOW,
            "decided_by_user_id": "customer-1",
            "decided_at": NOW,
            "decision_note": None,
            "withdrawn_at": None,
            "created_at": NOW,
        }
        fields.update(overrides)
        application = ProjectApplication(**fields)  # type: ignore[arg-type]
        await application_repo.add(application)
        return application

    return _make


@pytest.fixture
def make_delivery(delivery_repo: FakeProjectDeliveryRepository):
    async def _make(
        delivery_id: str = "delivery-1", status: DeliveryStatus = DeliveryStatus.SUBMITTED
    ) -> ProjectDelivery:
        delivery = ProjectDelivery(
            id=delivery_id,
            project_id="project-1",
            version_no=1,
            submitted_by_user_id="freelancer-1",
            status=status,
            delivery_note="v1",
            submitted_at=NOW,
            reviewed_at=None,
            reviewer_user_id=None,
            superseded_by_delivery_id=None,
            file_asset_ids=[],
            created_at=NOW,
        )
        await delivery_repo.add(delivery)
        return delivery

    return _make


@pytest.fixture
def make_customer_review(customer_review_repo: FakeCustomerReviewRepository):
    async def _make(
        review_id: str = "review-1",
        decision: ReviewStatus = ReviewStatus.APPROVED,
        **overrides: object,
    ) -> CustomerReview:
        fields: dict[str, object] = {
            "id": review_id,
            "project_id": "project-1",
            "project_delivery_id": "delivery-1",
            "customer_user_id": "customer-1",
            "decision": decision,
            "comment": None,
            "reviewed_at": NOW,
            "created_at": NOW,
        }
        fields.update(overrides)
        review = CustomerReview(**fields)  # type: ignore[arg-type]
        await customer_review_repo.add(review)
        return review

    return _make


@pytest.fixture
def make_rating(rating_repo: FakeRatingRepository):
    async def _make(rating_id: str = "rating-1", **overrides: object) -> Rating:
        fields: dict[str, object] = {
            "id": rating_id,
            "customer_review_id": "review-1",
            "project_id": "project-1",
            "customer_user_id": "customer-1",
            "freelancer_profile_id": "profile-1",
            "score": 5,
            "comment": None,
            "is_public": False,
            "created_at": NOW,
        }
        fields.update(overrides)
        rating = Rating(**fields)  # type: ignore[arg-type]
        await rating_repo.add(rating)
        return rating

    return _make
