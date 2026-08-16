from datetime import UTC, datetime
from decimal import Decimal

import pytest

from app.domain.form.entities import FormTemplate
from app.domain.form.enums import FormTemplateStatus
from app.domain.project.entities import Project
from app.domain.project.enums import BudgetType, ProjectPriority, ProjectStatus, ProjectVisibility
from app.domain.project.value_objects import Budget, ProjectCode
from tests.fakes.fake_form_template_repository import FakeFormTemplateRepository
from tests.fakes.fake_project_repository import FakeProjectRepository

NOW = datetime(2026, 8, 2, tzinfo=UTC)


@pytest.fixture
def template_repo() -> FakeFormTemplateRepository:
    return FakeFormTemplateRepository()


@pytest.fixture
def make_template(template_repo: FakeFormTemplateRepository):
    async def _make(
        template_id: str = "template-1",
        category_id: str = "cat-1",
        **overrides: object,
    ) -> FormTemplate:
        fields: dict[str, object] = {
            "id": template_id,
            "category_id": category_id,
            "template_key": "project-form",
            "name": "Project Form",
            "version_no": 1,
            "status": FormTemplateStatus.DRAFT,
            "is_active": True,
            "published_by_user_id": None,
            "published_at": None,
            "fields": [],
            "deleted_at": None,
            "created_at": NOW,
        }
        fields.update(overrides)
        template = FormTemplate(**fields)  # type: ignore[arg-type]
        await template_repo.add(template)
        return template

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
