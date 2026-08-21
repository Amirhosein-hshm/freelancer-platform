"""Presentation tests for the DRAFT-only project edit/delete routes (task §1).

Covers `PATCH /api/v1/projects/{id}` and `DELETE /api/v1/projects/{id}`: the envelope shape,
the 409 conflict once a project has moved past DRAFT, and that a deleted draft 404s
afterwards (soft-delete filtering, §12.6).
"""

from datetime import UTC, datetime
from decimal import Decimal

import pytest

from app.domain.form.entities import FormField, FormTemplate
from app.domain.form.enums import FormFieldType, FormTemplateStatus
from app.domain.project.entities import Project
from app.domain.project.enums import (
    BudgetType,
    ProjectPriority,
    ProjectStatus,
    ProjectVisibility,
)
from app.domain.project.value_objects import Budget, ProjectCode
from app.presentation.core import providers
from tests.presentation.conftest import auth_header

NOW = datetime(2026, 8, 2, tzinfo=UTC)
CUSTOMER = "customer-1"


async def _seed(overrides, status: ProjectStatus = ProjectStatus.DRAFT) -> None:
    project_repo = overrides[providers.get_project_repository]
    template_repo = overrides[providers.get_form_template_repository]
    authz = overrides[providers.get_authorization_service]
    authz.grant(CUSTOMER, "project.manage_own")
    await template_repo.add(
        FormTemplate(
            id="template-1",
            category_id="cat-1",
            template_key="project-form",
            name="Project Form",
            version_no=1,
            status=FormTemplateStatus.PUBLISHED,
            is_active=True,
            published_by_user_id="admin-1",
            published_at=NOW,
            fields=[
                FormField(
                    id="field-1",
                    field_key="title",
                    label="Title",
                    description=None,
                    field_type=FormFieldType.TEXT,
                    is_required=True,
                    is_repeatable=False,
                    is_unique=False,
                    sort_order=0,
                    validation_rules=None,
                    created_at=NOW,
                )
            ],
            created_at=NOW,
        )
    )
    await project_repo.add(
        Project(
            id="project-1",
            project_code=ProjectCode("PRJ-2026-001"),
            customer_user_id=CUSTOMER,
            category_id="cat-1",
            form_template_id="template-1",
            assigned_supervisor_user_id="supervisor-1",
            selected_application_id=None,
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
            status=status,
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


def _payload() -> dict:
    return {
        "title": "Updated title",
        "description": "Updated description",
        "visibility": "private",
        "budget_type": "fixed",
        "currency_code": "EUR",
        "fixed_budget": "2500",
        "priority": "high",
        "form_values": [{"field_id": "field-1", "value": "A title"}],
    }


@pytest.fixture
def headers(overrides) -> dict[str, str]:
    return auth_header(overrides[providers.get_token_service], CUSTOMER, ["customer"])


class TestUpdateProjectRoute:
    async def test_patch_draft_returns_success_envelope(self, client, overrides, headers):
        await _seed(overrides)

        response = client.patch("/api/v1/projects/project-1", json=_payload(), headers=headers)

        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert body["data"]["project_id"] == "project-1"
        assert body["data"]["status"] == ProjectStatus.DRAFT.value

    async def test_patch_past_draft_returns_409_envelope(self, client, overrides, headers):
        await _seed(overrides, status=ProjectStatus.PUBLISHED)

        response = client.patch("/api/v1/projects/project-1", json=_payload(), headers=headers)

        assert response.status_code == 409
        error = response.json()["error"]
        assert error["code"] == "PROJECT_NOT_DRAFT"
        assert "Cancel the project instead" in error["message"]

    async def test_patch_requires_auth(self, client, overrides):
        await _seed(overrides)

        response = client.patch("/api/v1/projects/project-1", json=_payload())

        assert response.status_code == 401


class TestDeleteProjectRoute:
    async def test_delete_draft_then_404_on_read(self, client, overrides, headers):
        await _seed(overrides)

        response = client.delete("/api/v1/projects/project-1", headers=headers)

        assert response.status_code == 200
        body = response.json()
        assert body["success"] is True
        assert body["data"]["project_id"] == "project-1"
        assert body["data"]["deleted_at"] is not None
        # Soft-deleted drafts stop surfacing.
        assert client.get("/api/v1/projects/project-1", headers=headers).status_code == 404

    async def test_delete_past_draft_returns_409(self, client, overrides, headers):
        await _seed(overrides, status=ProjectStatus.IN_PROGRESS)

        response = client.delete("/api/v1/projects/project-1", headers=headers)

        assert response.status_code == 409
        assert response.json()["error"]["code"] == "PROJECT_NOT_DRAFT"

    async def test_delete_requires_auth(self, client, overrides):
        await _seed(overrides)

        response = client.delete("/api/v1/projects/project-1")

        assert response.status_code == 401
