"""Repository add + get_by_id round-trip tests per bounded context.

Per TESTING.md §8 each bounded context must have at least one repository whose
``add`` then ``get_by_id`` (or closest equivalent read) persists and reads back
through a real Postgres.
"""

from datetime import UTC, datetime
from decimal import Decimal

import pytest

from app.domain.category.entities import Category
from app.domain.feedback.entities import CustomerReview, Rating
from app.domain.form.entities import FormField, FormTemplate
from app.domain.form.enums import FormFieldType, FormTemplateStatus
from app.domain.freelancer.entities import (
    FreelancerLevel,
    FreelancerProfile,
)
from app.domain.freelancer.enums import (
    FreelancerApprovalStatus,
    FreelancerLevelAccessType,
)
from app.domain.iam.entities import User
from app.domain.iam.enums import UserStatus
from app.domain.iam.value_objects import Email, PasswordHash
from app.domain.project.entities import (
    Project,
    ProjectApplication,
    ProjectDelivery,
    ProjectStatusHistory,
)
from app.domain.project.enums import (
    BudgetType,
    DeliveryStatus,
    ProjectApplicationStatus,
    ProjectPriority,
    ProjectStatus,
    ProjectVisibility,
)
from app.domain.project.value_objects import Budget, ProjectCode
from app.domain.review.entities import SupervisorReview
from app.domain.review.enums import ReviewStatus
from app.domain.ticketing.entities import Ticket
from app.domain.ticketing.enums import TicketPriority, TicketStatus
from app.infrastructure.db.models.freelancer_models import FreelancerLevelModel
from app.infrastructure.repositories.category_repository import (
    SqlAlchemyCategoryRepository,
)
from app.infrastructure.repositories.customer_review_repository import (
    SqlAlchemyCustomerReviewRepository,
)
from app.infrastructure.repositories.form_template_repository import (
    SqlAlchemyFormTemplateRepository,
)
from app.infrastructure.repositories.freelancer_profile_repository import (
    SqlAlchemyFreelancerProfileRepository,
)
from app.infrastructure.repositories.project_application_repository import (
    SqlAlchemyProjectApplicationRepository,
)
from app.infrastructure.repositories.project_delivery_repository import (
    SqlAlchemyProjectDeliveryRepository,
)
from app.infrastructure.repositories.project_repository import (
    SqlAlchemyProjectRepository,
)
from app.infrastructure.repositories.project_status_history_repository import (
    SqlAlchemyProjectStatusHistoryRepository,
)
from app.infrastructure.repositories.rating_repository import SqlAlchemyRatingRepository
from app.infrastructure.repositories.supervisor_review_repository import (
    SqlAlchemySupervisorReviewRepository,
)
from app.infrastructure.repositories.ticket_repository import SqlAlchemyTicketRepository
from app.infrastructure.repositories.user_repository import SqlAlchemyUserRepository

pytestmark = pytest.mark.integration


def _now() -> datetime:
    return datetime(2026, 8, 2, tzinfo=UTC)


def _user() -> User:
    return User(
        id="user-1",
        created_at=_now(),
        email=Email("test@example.com"),
        phone=None,
        password_hash=PasswordHash("hash"),
        first_name="Jane",
        last_name="Doe",
        status=UserStatus.ACTIVE,
    )


def _category() -> Category:
    return Category(
        id="cat-1",
        created_at=_now(),
        parent_category_id=None,
        category_key="web",
        name="Web",
        slug="web",
    )


def _level() -> FreelancerLevel:
    return FreelancerLevel(
        id="lvl-1",
        created_at=_now(),
        level_key="junior",
        name="Junior",
        rank_order=1,
        access_type=FreelancerLevelAccessType.STANDARD,
        min_completed_projects=0,
        min_rating=None,
        max_active_applications=5,
        can_apply_public_projects=True,
        can_apply_private_projects=False,
        is_active=True,
    )


def _profile() -> FreelancerProfile:
    return FreelancerProfile(
        id="prof-1",
        created_at=_now(),
        user_id="user-1",
        current_level_id=None,
        approval_status=FreelancerApprovalStatus.PENDING,
        approved_by_user_id=None,
        approved_at=None,
        approval_note=None,
        display_name="Jane Doe",
        headline=None,
        bio=None,
        country_code=None,
        city=None,
        timezone=None,
        hourly_rate_min=None,
        hourly_rate_max=None,
        is_available=True,
        deleted_at=None,
    )


def _template() -> FormTemplate:
    return FormTemplate(
        id="tmpl-1",
        created_at=_now(),
        category_id="cat-1",
        template_key="default",
        name="Default",
        version_no=1,
        status=FormTemplateStatus.DRAFT,
        is_active=True,
        published_by_user_id=None,
        published_at=None,
        fields=[
            FormField(
                id="field-1",
                created_at=_now(),
                field_key="title",
                label="Title",
                description=None,
                field_type=FormFieldType.TEXT,
                is_required=True,
                is_repeatable=False,
                is_unique=False,
                sort_order=1,
                validation_rules=None,
            )
        ],
    )


def _project() -> Project:
    return Project(
        id="proj-1",
        created_at=_now(),
        project_code=ProjectCode("PRJ-2026-001"),
        customer_user_id="user-1",
        category_id="cat-1",
        form_template_id="tmpl-1",
        assigned_supervisor_user_id=None,
        selected_application_id=None,
        title="Build a site",
        description="A project.",
        visibility=ProjectVisibility.PUBLIC,
        priority=ProjectPriority.NORMAL,
        budget=Budget(
            budget_type=BudgetType.FIXED,
            fixed_amount=Decimal("1000.00"),
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


def _application() -> ProjectApplication:
    return ProjectApplication(
        id="app-1",
        created_at=_now(),
        project_id="proj-1",
        freelancer_profile_id="prof-1",
        status=ProjectApplicationStatus.APPLIED,
        cover_letter=None,
        proposed_amount=None,
        proposed_days=None,
        applied_at=_now(),
        decided_by_user_id=None,
        decided_at=None,
        decision_note=None,
        withdrawn_at=None,
        submitted_by_user_id=None,
    )


def _delivery() -> ProjectDelivery:
    return ProjectDelivery(
        id="deliv-1",
        created_at=_now(),
        project_id="proj-1",
        version_no=1,
        submitted_by_user_id="user-1",
        status=DeliveryStatus.SUBMITTED,
        delivery_note=None,
        submitted_at=_now(),
        reviewed_at=None,
        reviewer_user_id=None,
        superseded_by_delivery_id=None,
        file_asset_ids=[],
    )


def _history() -> ProjectStatusHistory:
    return ProjectStatusHistory(
        id="hist-1",
        created_at=_now(),
        project_id="proj-1",
        from_status=ProjectStatus.DRAFT,
        to_status=ProjectStatus.PUBLISHED,
        changed_by_user_id="user-1",
        reason=None,
        changed_at=_now(),
    )


def _review() -> SupervisorReview:
    return SupervisorReview(
        id="rev-1",
        created_at=_now(),
        project_delivery_id="deliv-1",
        project_id="proj-1",
        supervisor_user_id="user-1",
        decision=ReviewStatus.PENDING,
    )


def _customer_review() -> CustomerReview:
    return CustomerReview(
        id="crev-1",
        created_at=_now(),
        project_id="proj-1",
        project_delivery_id="deliv-1",
        customer_user_id="user-1",
        decision=ReviewStatus.APPROVED,
        comment="Great",
        reviewed_at=_now(),
    )


def _rating() -> Rating:
    return Rating(
        id="rating-1",
        created_at=_now(),
        customer_review_id="crev-1",
        project_id="proj-1",
        customer_user_id="user-1",
        freelancer_profile_id="prof-1",
        score=5,
        comment="Nice",
        is_public=True,
    )


def _ticket() -> Ticket:
    return Ticket(
        id="ticket-1",
        created_at=_now(),
        ticket_code="TCK-2026-001",
        created_by_user_id="user-1",
        assigned_to_user_id=None,
        related_project_id=None,
        related_category_id=None,
        subject="Help",
        status=TicketStatus.OPEN,
        priority=TicketPriority.NORMAL,
        closed_by_user_id=None,
        closed_at=None,
        last_message_at=None,
        deleted_at=None,
        submitted_by_user_id=None,
    )


async def _seed_base(db_session) -> None:
    """Persist the shared FK dependency chain: user, category, level, template,
    project, application, delivery, profile."""
    await SqlAlchemyUserRepository(db_session).add(_user())
    await SqlAlchemyCategoryRepository(db_session).add(_category())
    await db_session.flush()
    db_session.add(
        FreelancerLevelModel(
            id="lvl-1",
            level_key="junior",
            name="Junior",
            rank_order=1,
            access_type="standard",
            min_completed_projects=0,
            min_rating=None,
            max_active_applications=5,
            can_apply_public_projects=True,
            can_apply_private_projects=False,
            is_active=True,
        )
    )
    await SqlAlchemyFreelancerProfileRepository(db_session).add(_profile())
    await SqlAlchemyFormTemplateRepository(db_session).add(_template())
    await SqlAlchemyProjectRepository(db_session).add(_project())
    await db_session.flush()
    await SqlAlchemyProjectApplicationRepository(db_session).add(_application())
    await SqlAlchemyProjectDeliveryRepository(db_session).add(_delivery())
    await db_session.commit()


async def test_user_repository_round_trip(db_session) -> None:
    repo = SqlAlchemyUserRepository(db_session)
    await repo.add(_user())
    await db_session.commit()
    loaded = await repo.get_by_id("user-1")
    assert loaded.email.value == "test@example.com"
    assert loaded.status == UserStatus.ACTIVE


async def test_category_repository_round_trip(db_session) -> None:
    repo = SqlAlchemyCategoryRepository(db_session)
    await repo.add(_category())
    await db_session.commit()
    assert (await repo.get_by_id("cat-1")).name == "Web"
    assert (await repo.get_by_slug("web")).category_key == "web"


async def test_form_template_repository_round_trip(db_session) -> None:
    await SqlAlchemyCategoryRepository(db_session).add(_category())
    repo = SqlAlchemyFormTemplateRepository(db_session)
    await repo.add(_template())
    await db_session.commit()
    loaded = await repo.get_by_id("tmpl-1")
    assert loaded.template_key == "default"
    assert loaded.fields[0].field_key == "title"


async def test_project_repository_round_trip(db_session) -> None:
    await SqlAlchemyUserRepository(db_session).add(_user())
    await SqlAlchemyCategoryRepository(db_session).add(_category())
    repo = SqlAlchemyProjectRepository(db_session)
    await repo.add(_project())
    await db_session.commit()
    loaded = await repo.get_by_id("proj-1")
    assert loaded.title == "Build a site"
    assert loaded.project_code.value == "PRJ-2026-001"
    by_code = await repo.get_by_code(ProjectCode("PRJ-2026-001"))
    assert by_code.id == "proj-1"


async def test_project_status_history_round_trip(db_session) -> None:
    await SqlAlchemyUserRepository(db_session).add(_user())
    await SqlAlchemyCategoryRepository(db_session).add(_category())
    await SqlAlchemyProjectRepository(db_session).add(_project())
    repo = SqlAlchemyProjectStatusHistoryRepository(db_session)
    await repo.add(_history())
    await db_session.commit()
    loaded = await repo.list_by_project("proj-1")
    assert len(loaded) == 1
    assert loaded[0].from_status == ProjectStatus.DRAFT


async def test_supervisor_review_repository_round_trip(db_session) -> None:
    await _seed_base(db_session)
    repo = SqlAlchemySupervisorReviewRepository(db_session)
    await repo.add(_review())
    await db_session.commit()
    loaded = await repo.get_by_delivery("deliv-1")
    assert loaded.project_id == "proj-1"
    assert loaded.decision == ReviewStatus.PENDING


async def test_customer_review_repository_round_trip(db_session) -> None:
    await _seed_base(db_session)
    repo = SqlAlchemyCustomerReviewRepository(db_session)
    await repo.add(_customer_review())
    await db_session.commit()
    loaded = await repo.find_by_project("proj-1")
    assert loaded is not None
    assert loaded.decision == ReviewStatus.APPROVED


async def test_rating_repository_round_trip(db_session) -> None:
    await _seed_base(db_session)
    review_repo = SqlAlchemyCustomerReviewRepository(db_session)
    await review_repo.add(_customer_review())
    await db_session.commit()
    repo = SqlAlchemyRatingRepository(db_session)
    await repo.add(_rating())
    await db_session.commit()
    found = await repo.find_by_project("proj-1")
    assert found is not None
    assert found.score == 5
    assert await repo.average_score_for_freelancer("prof-1") == Decimal("5.00")


async def test_ticket_repository_round_trip(db_session) -> None:
    await SqlAlchemyUserRepository(db_session).add(_user())
    repo = SqlAlchemyTicketRepository(db_session)
    await repo.add(_ticket())
    await db_session.commit()
    loaded = await repo.get_by_id("ticket-1")
    assert loaded.subject == "Help"
    assert (await repo.get_by_code("TCK-2026-001")).id == "ticket-1"
