from decimal import Decimal

import pytest

from app.application.project.dto import (
    CreateProjectCommand,
    FormValueInput,
)
from app.application.project.use_cases.create_project import CreateProjectUseCase
from app.application.shared.exceptions import FormValidationError, PermissionDeniedError
from app.domain.category.exceptions import CategoryNotFoundError
from app.domain.form.entities import FormField, FormTemplate
from app.domain.form.enums import FormFieldType, FormTemplateStatus
from app.domain.form.exceptions import FormTemplateNotFoundError
from app.domain.project.enums import BudgetType, ProjectStatus, ProjectVisibility
from tests.application.project.conftest import NOW


def seed_published_template(template_repo) -> FormTemplate:
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
            FormField(
                id="field-2",
                field_key="budget",
                label="Budget",
                description=None,
                field_type=FormFieldType.DECIMAL,
                is_required=True,
                is_repeatable=False,
                is_unique=False,
                sort_order=1,
                validation_rules=None,
                created_at=NOW,
            ),
        ],
        created_at=NOW,
    )
    template_repo.add(template)
    return template


def build_use_case(
    authorization_service,
    project_repo,
    category_repo,
    form_template_repo,
    status_history_repo,
    project_code_generator,
    id_generator,
    clock,
    uow,
) -> CreateProjectUseCase:
    return CreateProjectUseCase(
        authorization_service=authorization_service,
        project_repo=project_repo,
        category_repo=category_repo,
        form_template_repo=form_template_repo,
        status_history_repo=status_history_repo,
        project_code_generator=project_code_generator,
        id_generator=id_generator,
        clock=clock,
        uow=uow,
    )


def base_command(**overrides: object) -> CreateProjectCommand:
    fields: dict[str, object] = {
        "actor_id": "customer-1",
        "category_id": "cat-1",
        "title": "Build an API",
        "description": "REST API for orders",
        "visibility": ProjectVisibility.PUBLIC,
        "budget_type": BudgetType.FIXED,
        "currency_code": "USD",
        "fixed_budget": Decimal("1000"),
        "form_values": [
            FormValueInput(field_id="field-1", value="Order service"),
            FormValueInput(field_id="field-2", value="500"),
        ],
    }
    fields.update(overrides)
    return CreateProjectCommand(**fields)  # type: ignore[arg-type]


class TestCreateProjectUseCase:
    def test_create_project_succeeds(
        self,
        authorization_service,
        project_repo,
        category_repo,
        form_template_repo,
        status_history_repo,
        project_code_generator,
        id_generator,
        clock,
        uow,
        make_category,
    ):
        authorization_service.grant("customer-1", "project.create_own")
        make_category(category_id="cat-1")
        seed_published_template(form_template_repo)
        use_case = build_use_case(
            authorization_service,
            project_repo,
            category_repo,
            form_template_repo,
            status_history_repo,
            project_code_generator,
            id_generator,
            clock,
            uow,
        )

        result = use_case.execute(base_command())

        project = project_repo.get_by_id(result.project_id)
        assert result.status == ProjectStatus.DRAFT
        assert project.project_code.value.startswith("PRJ-2026-")
        assert project.customer_user_id == "customer-1"
        assert project.created_by_user_id == "customer-1"
        assert project.form_template_id == "template-1"
        assert uow.committed is True
        assert len(status_history_repo.list_by_project(project.id)) == 1

    def test_create_project_without_permission_raises(
        self,
        authorization_service,
        project_repo,
        category_repo,
        form_template_repo,
        status_history_repo,
        project_code_generator,
        id_generator,
        clock,
        uow,
        make_category,
    ):
        make_category(category_id="cat-1")
        use_case = build_use_case(
            authorization_service,
            project_repo,
            category_repo,
            form_template_repo,
            status_history_repo,
            project_code_generator,
            id_generator,
            clock,
            uow,
        )

        with pytest.raises(PermissionDeniedError):
            use_case.execute(base_command())

    def test_unknown_category_raises(
        self,
        authorization_service,
        project_repo,
        category_repo,
        form_template_repo,
        status_history_repo,
        project_code_generator,
        id_generator,
        clock,
        uow,
    ):
        authorization_service.grant("customer-1", "project.create_own")
        use_case = build_use_case(
            authorization_service,
            project_repo,
            category_repo,
            form_template_repo,
            status_history_repo,
            project_code_generator,
            id_generator,
            clock,
            uow,
        )

        with pytest.raises(CategoryNotFoundError):
            use_case.execute(base_command())

    def test_missing_published_template_raises(
        self,
        authorization_service,
        project_repo,
        category_repo,
        form_template_repo,
        status_history_repo,
        project_code_generator,
        id_generator,
        clock,
        uow,
        make_category,
    ):
        authorization_service.grant("customer-1", "project.create_own")
        make_category(category_id="cat-1")
        use_case = build_use_case(
            authorization_service,
            project_repo,
            category_repo,
            form_template_repo,
            status_history_repo,
            project_code_generator,
            id_generator,
            clock,
            uow,
        )

        with pytest.raises(FormTemplateNotFoundError):
            use_case.execute(base_command())

    def test_missing_required_field_value_raises_form_validation(
        self,
        authorization_service,
        project_repo,
        category_repo,
        form_template_repo,
        status_history_repo,
        project_code_generator,
        id_generator,
        clock,
        uow,
        make_category,
    ):
        authorization_service.grant("customer-1", "project.create_own")
        make_category(category_id="cat-1")
        seed_published_template(form_template_repo)
        use_case = build_use_case(
            authorization_service,
            project_repo,
            category_repo,
            form_template_repo,
            status_history_repo,
            project_code_generator,
            id_generator,
            clock,
            uow,
        )

        with pytest.raises(FormValidationError):
            use_case.execute(base_command(form_values=[]))

    def test_invalid_decimal_raises_form_validation(
        self,
        authorization_service,
        project_repo,
        category_repo,
        form_template_repo,
        status_history_repo,
        project_code_generator,
        id_generator,
        clock,
        uow,
        make_category,
    ):
        authorization_service.grant("customer-1", "project.create_own")
        make_category(category_id="cat-1")
        seed_published_template(form_template_repo)
        use_case = build_use_case(
            authorization_service,
            project_repo,
            category_repo,
            form_template_repo,
            status_history_repo,
            project_code_generator,
            id_generator,
            clock,
            uow,
        )

        with pytest.raises(FormValidationError):
            use_case.execute(
                base_command(
                    form_values=[
                        FormValueInput(field_id="field-1", value="Order service"),
                        FormValueInput(field_id="field-2", value="not-a-number"),
                    ]
                )
            )
