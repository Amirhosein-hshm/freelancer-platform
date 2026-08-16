from datetime import UTC, datetime
from decimal import Decimal

import pytest

from app.domain.project.entities import Project
from app.domain.project.enums import (
    BudgetType,
    ProjectPriority,
    ProjectStatus,
    ProjectVisibility,
)
from app.domain.project.exceptions import (
    InvalidProjectStatusTransitionError,
    ProjectAlreadyAssignedError,
    ProjectLockedError,
)
from app.domain.project.value_objects import Budget, ProjectCode

NOW = datetime(2026, 8, 2, tzinfo=UTC)


def make_project(**overrides: object) -> Project:
    fields: dict[str, object] = {
        "id": "project-1",
        "project_code": ProjectCode("PRJ-2026-001"),
        "customer_user_id": "customer-1",
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
        "status": ProjectStatus.DRAFT,
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
    return Project(**fields)  # type: ignore[arg-type]


class TestPublish:
    def test_draft_to_published(self):
        project = make_project()
        project.publish(NOW)
        assert project.status == ProjectStatus.PUBLISHED

    def test_publish_from_non_draft_raises(self):
        project = make_project(status=ProjectStatus.IN_PROGRESS)
        with pytest.raises(InvalidProjectStatusTransitionError):
            project.publish(NOW)

    def test_publish_locked_raises(self):
        project = make_project(status=ProjectStatus.COMPLETED)
        with pytest.raises(ProjectLockedError):
            project.publish(NOW)


class TestCollectingApplications:
    def test_published_to_collecting(self):
        project = make_project(status=ProjectStatus.PUBLISHED)
        project.start_collecting_applications()
        assert project.status == ProjectStatus.COLLECTING_APPLICATIONS
        assert project.can_accept_applications() is True

    def test_wrong_from_state_raises(self):
        project = make_project(status=ProjectStatus.DRAFT)
        with pytest.raises(InvalidProjectStatusTransitionError):
            project.start_collecting_applications()


class TestAssignFreelancer:
    def test_assign_sets_selection_and_status(self):
        project = make_project(status=ProjectStatus.COLLECTING_APPLICATIONS)
        project.assign_freelancer("app-1", NOW)
        assert project.status == ProjectStatus.ASSIGNED
        assert project.selected_application_id == "app-1"
        assert project.can_accept_applications() is False

    def test_assign_twice_raises(self):
        project = make_project(status=ProjectStatus.COLLECTING_APPLICATIONS, selected_application_id="app-1")
        with pytest.raises(ProjectAlreadyAssignedError):
            project.assign_freelancer("app-2", NOW)


class TestStart:
    def test_assigned_to_in_progress(self):
        project = make_project(status=ProjectStatus.ASSIGNED, selected_application_id="app-1")
        project.start(NOW)
        assert project.status == ProjectStatus.IN_PROGRESS
        assert project.start_at == NOW

    def test_wrong_from_state_raises(self):
        project = make_project(status=ProjectStatus.DRAFT)
        with pytest.raises(InvalidProjectStatusTransitionError):
            project.start(NOW)


class TestDeliveryFlow:
    def test_in_progress_to_delivery_submitted(self):
        project = make_project(status=ProjectStatus.IN_PROGRESS)
        project.mark_delivery_submitted()
        assert project.status == ProjectStatus.DELIVERY_SUBMITTED

    def test_revision_requested_to_delivery_submitted(self):
        project = make_project(status=ProjectStatus.REVISION_REQUESTED)
        project.mark_delivery_submitted()
        assert project.status == ProjectStatus.DELIVERY_SUBMITTED

    def test_delivery_submitted_from_wrong_state_raises(self):
        project = make_project(status=ProjectStatus.DRAFT)
        with pytest.raises(InvalidProjectStatusTransitionError):
            project.mark_delivery_submitted()

    def test_move_to_supervisor_review(self):
        project = make_project(status=ProjectStatus.DELIVERY_SUBMITTED)
        project.move_to_supervisor_review()
        assert project.status == ProjectStatus.UNDER_SUPERVISOR_REVIEW

    def test_move_to_supervisor_review_without_supervisor_raises(self):
        project = make_project(status=ProjectStatus.DELIVERY_SUBMITTED, assigned_supervisor_user_id=None)
        with pytest.raises(InvalidProjectStatusTransitionError):
            project.move_to_supervisor_review()

    def test_move_to_customer_review_directly(self):
        project = make_project(status=ProjectStatus.DELIVERY_SUBMITTED, assigned_supervisor_user_id=None)
        project.move_to_customer_review()
        assert project.status == ProjectStatus.AWAITING_CUSTOMER_REVIEW

    def test_move_to_customer_review_after_supervisor(self):
        project = make_project(status=ProjectStatus.UNDER_SUPERVISOR_REVIEW)
        project.move_to_customer_review()
        assert project.status == ProjectStatus.AWAITING_CUSTOMER_REVIEW

    def test_move_to_customer_review_wrong_state_raises(self):
        project = make_project(status=ProjectStatus.DRAFT)
        with pytest.raises(InvalidProjectStatusTransitionError):
            project.move_to_customer_review()


class TestRequestRevision:
    def test_from_supervisor_review(self):
        project = make_project(status=ProjectStatus.UNDER_SUPERVISOR_REVIEW)
        project.request_revision()
        assert project.status == ProjectStatus.REVISION_REQUESTED

    def test_from_customer_review(self):
        project = make_project(status=ProjectStatus.AWAITING_CUSTOMER_REVIEW)
        project.request_revision()
        assert project.status == ProjectStatus.REVISION_REQUESTED

    def test_from_wrong_state_raises(self):
        project = make_project(status=ProjectStatus.IN_PROGRESS)
        with pytest.raises(InvalidProjectStatusTransitionError):
            project.request_revision()


class TestComplete:
    def test_complete_sets_locked(self):
        project = make_project(status=ProjectStatus.AWAITING_CUSTOMER_REVIEW)
        project.complete(NOW)
        assert project.status == ProjectStatus.COMPLETED
        assert project.completed_at == NOW
        assert project.locked_at == NOW
        assert project.is_locked() is True

    def test_complete_wrong_state_raises(self):
        project = make_project(status=ProjectStatus.DRAFT)
        with pytest.raises(InvalidProjectStatusTransitionError):
            project.complete(NOW)


class TestCancel:
    def test_cancel_draft(self):
        project = make_project()
        project.cancel(NOW, "No longer needed")
        assert project.status == ProjectStatus.CANCELLED
        assert project.cancelled_at == NOW

    def test_cancel_in_progress(self):
        project = make_project(status=ProjectStatus.IN_PROGRESS)
        project.cancel(NOW, "Customer bailed")
        assert project.status == ProjectStatus.CANCELLED

    def test_cancel_completed_raises(self):
        project = make_project(status=ProjectStatus.COMPLETED)
        with pytest.raises(ProjectLockedError):
            project.cancel(NOW, "too late")

    def test_cancel_cancelled_raises(self):
        project = make_project(status=ProjectStatus.CANCELLED)
        with pytest.raises(ProjectLockedError):
            project.cancel(NOW, "again")


class TestHelpers:
    def test_is_locked_for_completed_and_cancelled(self):
        assert make_project(status=ProjectStatus.COMPLETED).is_locked() is True
        assert make_project(status=ProjectStatus.CANCELLED).is_locked() is True
        assert make_project(status=ProjectStatus.IN_PROGRESS).is_locked() is False

    def test_has_supervisor(self):
        assert make_project().has_supervisor() is True
        assert make_project(assigned_supervisor_user_id=None).has_supervisor() is False

    def test_can_accept_applications_states(self):
        assert make_project(status=ProjectStatus.PUBLISHED).can_accept_applications() is True
        assert make_project(status=ProjectStatus.COLLECTING_APPLICATIONS).can_accept_applications() is True
        assert make_project(status=ProjectStatus.ASSIGNED).can_accept_applications() is False
