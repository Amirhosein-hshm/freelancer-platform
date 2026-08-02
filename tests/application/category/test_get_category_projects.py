from datetime import UTC, datetime
from decimal import Decimal

import pytest

from app.application.category.use_cases.get_category_projects import (
    GetCategoryProjectsQuery,
    GetCategoryProjectsUseCase,
)
from app.domain.category.exceptions import CategoryNotFoundError
from app.domain.project.entities import Project
from app.domain.project.enums import (
    BudgetType,
    ProjectPriority,
    ProjectStatus,
    ProjectVisibility,
)
from app.domain.project.value_objects import Budget, ProjectCode
from tests.fakes.fake_project_repository import FakeProjectRepository

NOW = datetime(2026, 8, 2, tzinfo=UTC)


@pytest.fixture
def project_repo() -> FakeProjectRepository:
    return FakeProjectRepository()


@pytest.fixture
def make_project(project_repo: FakeProjectRepository):
    def _make(
        project_id: str = "project-1",
        category_id: str = "cat-1",
        status: ProjectStatus = ProjectStatus.COLLECTING_APPLICATIONS,
        **overrides: object,
    ) -> Project:
        fields: dict[str, object] = {
            "id": project_id,
            "project_code": ProjectCode("PRJ-2026-001"),
            "customer_user_id": "customer-1",
            "category_id": category_id,
            "form_template_id": "template-1",
            "assigned_supervisor_user_id": None,
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


class TestGetCategoryProjectsUseCase:
    def test_returns_open_projects_of_category(self, category_repo, project_repo, make_category, make_project):
        make_category(category_id="cat-1")
        make_project(project_id="project-1", category_id="cat-1", status=ProjectStatus.COLLECTING_APPLICATIONS)
        make_project(project_id="project-2", category_id="cat-1", status=ProjectStatus.PUBLISHED)
        make_project(project_id="project-3", category_id="cat-1", status=ProjectStatus.IN_PROGRESS)
        make_project(project_id="project-4", category_id="cat-2", status=ProjectStatus.COLLECTING_APPLICATIONS)
        use_case = GetCategoryProjectsUseCase(category_repo=category_repo, project_repo=project_repo)

        result = use_case.execute(GetCategoryProjectsQuery(category_id="cat-1"))

        assert [p.project_id for p in result.projects] == ["project-1", "project-2"]
        assert result.category_id == "cat-1"

    def test_unknown_category_raises(self, category_repo, project_repo):
        use_case = GetCategoryProjectsUseCase(category_repo=category_repo, project_repo=project_repo)

        with pytest.raises(CategoryNotFoundError):
            use_case.execute(GetCategoryProjectsQuery(category_id="missing"))
