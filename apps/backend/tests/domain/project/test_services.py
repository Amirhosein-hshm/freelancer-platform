from datetime import UTC, datetime
from decimal import Decimal

import pytest

from app.domain.freelancer.enums import FreelancerLevelEnum
from app.domain.project.entities import Project
from app.domain.project.enums import (
    BudgetType,
    ProjectPriority,
    ProjectStatus,
    ProjectVisibility,
)
from app.domain.project.exceptions import MaxRevisionsExceededError
from app.domain.project.services import FreelancerEligibilityPolicy, RevisionPolicy
from app.domain.project.value_objects import Budget, ProjectCode

NOW = datetime(2026, 8, 2, tzinfo=UTC)


def make_level(**overrides: object) -> FreelancerLevelEnum | None:
    if overrides.get("is_active", True) is False:
        return None
    return FreelancerLevelEnum.JUNIOR


def make_project(visibility: ProjectVisibility) -> Project:
    return Project(
        id="project-1",
        project_code=ProjectCode("PRJ-2026-001"),
        customer_user_id="customer-1",
        category_id="cat-1",
            form_template_id="template-1",
            required_level=None,
        selected_application_id=None,
        title="Build an API",
        description="REST API",
        visibility=visibility,
        priority=ProjectPriority.NORMAL,
        budget=Budget(
            budget_type=BudgetType.FIXED,
            fixed_amount=Decimal("1000"),
            min_amount=None,
            max_amount=None,
            currency_code="USD",
        ),
        status=ProjectStatus.COLLECTING_APPLICATIONS,
        application_deadline=None,
        start_at=None,
        due_at=None,
        completed_at=None,
        cancelled_at=None,
        locked_at=None,
        deleted_at=None,
        created_at=NOW,
    )


class TestRevisionPolicy:
    def test_allows_below_max(self):
        existing = [object()] * (RevisionPolicy.MAX_REVISIONS - 1)  # type: ignore[list-item]
        assert RevisionPolicy.can_request_new_revision(existing) is True  # type: ignore[arg-type]

    def test_blocks_at_max(self):
        existing = [object()] * RevisionPolicy.MAX_REVISIONS  # type: ignore[list-item]
        assert RevisionPolicy.can_request_new_revision(existing) is False  # type: ignore[arg-type]

    def test_ensure_below_max_passes(self):
        existing = [object()] * (RevisionPolicy.MAX_REVISIONS - 1)  # type: ignore[list-item]
        RevisionPolicy.ensure_can_request_new_revision(existing)  # type: ignore[arg-type]

    def test_ensure_at_max_raises(self):
        existing = [object()] * RevisionPolicy.MAX_REVISIONS  # type: ignore[list-item]
        with pytest.raises(MaxRevisionsExceededError):
            RevisionPolicy.ensure_can_request_new_revision(existing)  # type: ignore[arg-type]


class TestFreelancerEligibilityPolicy:
    def test_invite_only_is_not_self_applyable(self):
        level = FreelancerLevelEnum.JUNIOR
        assert (
            FreelancerEligibilityPolicy.is_eligible_to_apply(level, make_project(ProjectVisibility.INVITE_ONLY), 0)
            is False
        )

    def test_max_active_applications(self):
        level = FreelancerLevelEnum.JUNIOR
        assert (
            FreelancerEligibilityPolicy.is_eligible_to_apply(level, make_project(ProjectVisibility.PUBLIC), 10) is False
        )
        assert (
            FreelancerEligibilityPolicy.is_eligible_to_apply(level, make_project(ProjectVisibility.PUBLIC), 9) is True
        )

    def test_eligible(self):
        level = FreelancerLevelEnum.JUNIOR
        assert (
            FreelancerEligibilityPolicy.is_eligible_to_apply(level, make_project(ProjectVisibility.PUBLIC), 0) is True
        )
