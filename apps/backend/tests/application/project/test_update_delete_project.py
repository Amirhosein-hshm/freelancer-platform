from decimal import Decimal

import pytest

from app.application.project.dto import (
    DeleteProjectCommand,
    FormValueInput,
    UpdateProjectCommand,
)
from app.application.project.use_cases.delete_project import DeleteProjectUseCase
from app.application.project.use_cases.update_project import UpdateProjectUseCase
from app.application.shared.exceptions import (
    FormValidationError,
    PermissionDeniedError,
    ValidationError,
)
from app.domain.form.entities import FormField, FormTemplate
from app.domain.form.enums import FormFieldType, FormTemplateStatus
from app.domain.project.enums import (
    BudgetType,
    ProjectPriority,
    ProjectStatus,
    ProjectVisibility,
)
from app.domain.project.exceptions import ProjectNotDraftError, ProjectNotFoundError
from tests.application.project.conftest import NOW

PROJECT_MANAGE_OWN = "project.manage_own"
PROJECT_MANAGE_ANY = "project.manage_any"


async def seed_template(template_repo) -> FormTemplate:
    template = FormTemplate(
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
            ),
        ],
        created_at=NOW,
    )
    await template_repo.add(template)
    return template


def build_update(authorization_service, project_repo, form_template_repo, uow) -> UpdateProjectUseCase:
    return UpdateProjectUseCase(
        authorization_service=authorization_service,
        project_repo=project_repo,
        form_template_repo=form_template_repo,
        uow=uow,
    )


def build_delete(authorization_service, project_repo, clock, uow) -> DeleteProjectUseCase:
    return DeleteProjectUseCase(
        authorization_service=authorization_service,
        project_repo=project_repo,
        clock=clock,
        uow=uow,
    )


def update_command(**overrides) -> UpdateProjectCommand:
    fields: dict[str, object] = {
        "actor_id": "customer-1",
        "project_id": "project-1",
        "title": "Updated title",
        "description": "Updated description",
        "visibility": ProjectVisibility.PRIVATE,
        "budget_type": BudgetType.FIXED,
        "currency_code": "EUR",
        "fixed_budget": Decimal("2500"),
        "priority": ProjectPriority.HIGH,
        "form_values": [FormValueInput(field_id="field-1", value="A title")],
    }
    fields.update(overrides)
    return UpdateProjectCommand(**fields)  # type: ignore[arg-type]


class TestUpdateProjectUseCase:
    async def test_owner_can_update_draft_project(
        self, authorization_service, project_repo, form_template_repo, uow, make_project
    ):
        authorization_service.grant("customer-1", PROJECT_MANAGE_OWN)
        await make_project(status=ProjectStatus.DRAFT)
        await seed_template(form_template_repo)
        use_case = build_update(authorization_service, project_repo, form_template_repo, uow)

        result = await use_case.execute(update_command())

        assert result.project_id == "project-1"
        assert result.status == ProjectStatus.DRAFT
        assert uow.committed is True
        project = await project_repo.get_by_id("project-1")
        assert project.title == "Updated title"
        assert project.description == "Updated description"
        assert project.visibility == ProjectVisibility.PRIVATE
        assert project.priority == ProjectPriority.HIGH
        assert project.budget.fixed_amount == Decimal("2500")
        assert project.budget.currency_code == "EUR"

    async def test_admin_can_update_any_draft_project(
        self, authorization_service, project_repo, form_template_repo, uow, make_project
    ):
        authorization_service.grant("admin-1", PROJECT_MANAGE_ANY)
        await make_project(status=ProjectStatus.DRAFT)
        await seed_template(form_template_repo)
        use_case = build_update(authorization_service, project_repo, form_template_repo, uow)

        result = await use_case.execute(update_command(actor_id="admin-1"))

        assert result.project_id == "project-1"

    async def test_update_requires_permission(
        self, authorization_service, project_repo, form_template_repo, uow, make_project
    ):
        await make_project(status=ProjectStatus.DRAFT)
        await seed_template(form_template_repo)
        use_case = build_update(authorization_service, project_repo, form_template_repo, uow)

        with pytest.raises(PermissionDeniedError):
            await use_case.execute(update_command())

    async def test_non_owner_without_manage_any_is_denied(
        self, authorization_service, project_repo, form_template_repo, uow, make_project
    ):
        authorization_service.grant("stranger", PROJECT_MANAGE_OWN)
        await make_project(status=ProjectStatus.DRAFT)
        await seed_template(form_template_repo)
        use_case = build_update(authorization_service, project_repo, form_template_repo, uow)

        with pytest.raises(PermissionDeniedError):
            await use_case.execute(update_command(actor_id="stranger"))

    @pytest.mark.parametrize(
        "status",
        [
            ProjectStatus.PUBLISHED,
            ProjectStatus.COLLECTING_APPLICATIONS,
            ProjectStatus.ASSIGNED,
            ProjectStatus.IN_PROGRESS,
            ProjectStatus.COMPLETED,
            ProjectStatus.CANCELLED,
        ],
    )
    async def test_update_past_draft_is_rejected(
        self, authorization_service, project_repo, form_template_repo, uow, make_project, status
    ):
        authorization_service.grant("customer-1", PROJECT_MANAGE_OWN)
        await make_project(status=status)
        await seed_template(form_template_repo)
        use_case = build_update(authorization_service, project_repo, form_template_repo, uow)

        with pytest.raises(ProjectNotDraftError) as exc:
            await use_case.execute(update_command())

        assert "Cancel the project instead" in str(exc.value)
        assert uow.committed is False
        # Nothing was mutated.
        assert (await project_repo.get_by_id("project-1")).title == "Build an API"

    async def test_update_revalidates_form_values(
        self, authorization_service, project_repo, form_template_repo, uow, make_project
    ):
        authorization_service.grant("customer-1", PROJECT_MANAGE_OWN)
        await make_project(status=ProjectStatus.DRAFT)
        await seed_template(form_template_repo)
        use_case = build_update(authorization_service, project_repo, form_template_repo, uow)

        with pytest.raises(FormValidationError):
            await use_case.execute(update_command(form_values=[]))

    async def test_update_rejects_unknown_field_id(
        self, authorization_service, project_repo, form_template_repo, uow, make_project
    ):
        authorization_service.grant("customer-1", PROJECT_MANAGE_OWN)
        await make_project(status=ProjectStatus.DRAFT)
        await seed_template(form_template_repo)
        use_case = build_update(authorization_service, project_repo, form_template_repo, uow)

        with pytest.raises(FormValidationError):
            await use_case.execute(update_command(form_values=[FormValueInput(field_id="ghost", value="x")]))

    async def test_update_validates_command(
        self, authorization_service, project_repo, form_template_repo, uow, make_project
    ):
        authorization_service.grant("customer-1", PROJECT_MANAGE_OWN)
        await make_project(status=ProjectStatus.DRAFT)
        await seed_template(form_template_repo)
        use_case = build_update(authorization_service, project_repo, form_template_repo, uow)

        with pytest.raises(ValidationError):
            await use_case.execute(update_command(title="   "))

    async def test_update_unknown_project_raises(
        self, authorization_service, project_repo, form_template_repo, uow
    ):
        authorization_service.grant("customer-1", PROJECT_MANAGE_OWN)
        use_case = build_update(authorization_service, project_repo, form_template_repo, uow)

        with pytest.raises(ProjectNotFoundError):
            await use_case.execute(update_command())

    async def test_soft_deleted_project_cannot_be_updated(
        self, authorization_service, project_repo, form_template_repo, clock, uow, make_project
    ):
        authorization_service.grant("customer-1", PROJECT_MANAGE_OWN)
        await make_project(status=ProjectStatus.DRAFT)
        await seed_template(form_template_repo)
        await build_delete(authorization_service, project_repo, clock, uow).execute(
            DeleteProjectCommand(actor_id="customer-1", project_id="project-1")
        )
        use_case = build_update(authorization_service, project_repo, form_template_repo, uow)

        with pytest.raises(ProjectNotFoundError):
            await use_case.execute(update_command())


class TestDeleteProjectUseCase:
    async def test_owner_can_delete_draft_project(
        self, authorization_service, project_repo, clock, uow, make_project
    ):
        authorization_service.grant("customer-1", PROJECT_MANAGE_OWN)
        await make_project(status=ProjectStatus.DRAFT)
        use_case = build_delete(authorization_service, project_repo, clock, uow)

        result = await use_case.execute(DeleteProjectCommand(actor_id="customer-1", project_id="project-1"))

        assert result.project_id == "project-1"
        assert result.deleted_at == await clock.now()
        assert uow.committed is True
        # Soft-deleted: hidden from every read path.
        with pytest.raises(ProjectNotFoundError):
            await project_repo.get_by_id("project-1")
        assert await project_repo.list_by_customer("customer-1") == []

    async def test_admin_can_delete_any_draft_project(
        self, authorization_service, project_repo, clock, uow, make_project
    ):
        authorization_service.grant("admin-1", PROJECT_MANAGE_ANY)
        await make_project(status=ProjectStatus.DRAFT)
        use_case = build_delete(authorization_service, project_repo, clock, uow)

        result = await use_case.execute(DeleteProjectCommand(actor_id="admin-1", project_id="project-1"))

        assert result.project_id == "project-1"

    async def test_delete_requires_permission(self, authorization_service, project_repo, clock, uow, make_project):
        await make_project(status=ProjectStatus.DRAFT)
        use_case = build_delete(authorization_service, project_repo, clock, uow)

        with pytest.raises(PermissionDeniedError):
            await use_case.execute(DeleteProjectCommand(actor_id="customer-1", project_id="project-1"))

    async def test_non_owner_without_manage_any_is_denied(
        self, authorization_service, project_repo, clock, uow, make_project
    ):
        authorization_service.grant("stranger", PROJECT_MANAGE_OWN)
        await make_project(status=ProjectStatus.DRAFT)
        use_case = build_delete(authorization_service, project_repo, clock, uow)

        with pytest.raises(PermissionDeniedError):
            await use_case.execute(DeleteProjectCommand(actor_id="stranger", project_id="project-1"))

    @pytest.mark.parametrize(
        "status",
        [
            ProjectStatus.PUBLISHED,
            ProjectStatus.COLLECTING_APPLICATIONS,
            ProjectStatus.ASSIGNED,
            ProjectStatus.IN_PROGRESS,
            ProjectStatus.COMPLETED,
            ProjectStatus.CANCELLED,
        ],
    )
    async def test_delete_past_draft_is_rejected_and_points_at_cancel(
        self, authorization_service, project_repo, clock, uow, make_project, status
    ):
        authorization_service.grant("customer-1", PROJECT_MANAGE_OWN)
        await make_project(status=status)
        use_case = build_delete(authorization_service, project_repo, clock, uow)

        with pytest.raises(ProjectNotDraftError) as exc:
            await use_case.execute(DeleteProjectCommand(actor_id="customer-1", project_id="project-1"))

        assert "Cancel the project instead" in str(exc.value)
        assert uow.committed is False
        # Still readable: nothing was deleted.
        assert (await project_repo.get_by_id("project-1")).deleted_at is None

    async def test_delete_twice_raises_not_found(
        self, authorization_service, project_repo, clock, uow, make_project
    ):
        authorization_service.grant("customer-1", PROJECT_MANAGE_OWN)
        await make_project(status=ProjectStatus.DRAFT)
        use_case = build_delete(authorization_service, project_repo, clock, uow)
        await use_case.execute(DeleteProjectCommand(actor_id="customer-1", project_id="project-1"))

        with pytest.raises(ProjectNotFoundError):
            await use_case.execute(DeleteProjectCommand(actor_id="customer-1", project_id="project-1"))

    async def test_delete_unknown_project_raises(self, authorization_service, project_repo, clock, uow):
        authorization_service.grant("customer-1", PROJECT_MANAGE_OWN)
        use_case = build_delete(authorization_service, project_repo, clock, uow)

        with pytest.raises(ProjectNotFoundError):
            await use_case.execute(DeleteProjectCommand(actor_id="customer-1", project_id="ghost"))
