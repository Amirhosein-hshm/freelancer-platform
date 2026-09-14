import pytest

from app.application.form.dto import (
    RemoveFieldOptionCommand,
    UpdateFieldOptionCommand,
)
from app.application.form.use_cases.remove_field_option import RemoveFieldOptionUseCase
from app.application.form.use_cases.update_field_option import UpdateFieldOptionUseCase
from app.application.shared.exceptions import PermissionDeniedError
from app.domain.form.entities import FormField, FormFieldOption
from app.domain.form.enums import FormFieldType
from app.domain.form.exceptions import FieldNotFoundError, OptionNotFoundError


def build_update_use_case(authorization_service, template_repo, uow):
    return UpdateFieldOptionUseCase(authorization_service, template_repo, uow)


def build_remove_use_case(authorization_service, template_repo, uow):
    return RemoveFieldOptionUseCase(authorization_service, template_repo, uow)


class TestUpdateFieldOptionUseCase:
    async def test_update_option(self, authorization_service, template_repo, uow, make_template):
        authorization_service.grant("admin", "form.manage")
        option = FormFieldOption(
            id="option-1",
            option_key="opt1",
            label="Option 1",
            value="1",
            sort_order=0,
            is_active=True,
            created_at=None,  # type: ignore[arg-type]
        )
        field = FormField(
            id="field-1",
            field_key="select",
            label="Select",
            description=None,
            field_type=FormFieldType.SELECT,
            is_required=False,
            is_repeatable=False,
            is_unique=False,
            sort_order=0,
            validation_rules=None,
            options=[option],
            created_at=None,  # type: ignore[arg-type]
        )
        await make_template(template_id="template-1", fields=[field])
        use_case = build_update_use_case(authorization_service, template_repo, uow)

        result = await use_case.execute(
            UpdateFieldOptionCommand(
                actor_id="admin",
                template_id="template-1",
                field_id="field-1",
                option_id="option-1",
                label="Updated Option",
                sort_order=5,
            )
        )

        assert result.option_id == "option-1"
        updated = await template_repo.get_by_id("template-1")
        updated_option = updated.get_field("field-1").get_option("opt1")
        assert updated_option is not None
        assert updated_option.label == "Updated Option"
        assert updated_option.sort_order == 5

    async def test_update_option_requires_permission(self, authorization_service, template_repo, uow, make_template):
        await make_template(template_id="template-1")
        use_case = build_update_use_case(authorization_service, template_repo, uow)

        with pytest.raises(PermissionDeniedError):
            await use_case.execute(
                UpdateFieldOptionCommand(
                    actor_id="admin",
                    template_id="template-1",
                    field_id="field-1",
                    option_id="option-1",
                )
            )

    async def test_update_option_unknown_field(self, authorization_service, template_repo, uow, make_template):
        authorization_service.grant("admin", "form.manage")
        await make_template(template_id="template-1")
        use_case = build_update_use_case(authorization_service, template_repo, uow)

        with pytest.raises(FieldNotFoundError):
            await use_case.execute(
                UpdateFieldOptionCommand(
                    actor_id="admin",
                    template_id="template-1",
                    field_id="field-1",
                    option_id="option-1",
                )
            )


class TestRemoveFieldOptionUseCase:
    async def test_remove_option(self, authorization_service, template_repo, uow, make_template):
        authorization_service.grant("admin", "form.manage")
        option = FormFieldOption(
            id="option-1",
            option_key="opt1",
            label="Option 1",
            value="1",
            sort_order=0,
            is_active=True,
            created_at=None,  # type: ignore[arg-type]
        )
        field = FormField(
            id="field-1",
            field_key="select",
            label="Select",
            description=None,
            field_type=FormFieldType.SELECT,
            is_required=False,
            is_repeatable=False,
            is_unique=False,
            sort_order=0,
            validation_rules=None,
            options=[option],
            created_at=None,  # type: ignore[arg-type]
        )
        await make_template(template_id="template-1", fields=[field])
        use_case = build_remove_use_case(authorization_service, template_repo, uow)

        result = await use_case.execute(
            RemoveFieldOptionCommand(
                actor_id="admin",
                template_id="template-1",
                field_id="field-1",
                option_id="option-1",
            )
        )

        assert result.option_id == "option-1"
        updated = await template_repo.get_by_id("template-1")
        assert len(updated.get_field("field-1").options) == 0

    async def test_remove_unknown_option(self, authorization_service, template_repo, uow, make_template):
        authorization_service.grant("admin", "form.manage")
        field = FormField(
            id="field-1",
            field_key="select",
            label="Select",
            description=None,
            field_type=FormFieldType.SELECT,
            is_required=False,
            is_repeatable=False,
            is_unique=False,
            sort_order=0,
            validation_rules=None,
            options=[],
            created_at=None,  # type: ignore[arg-type]
        )
        await make_template(template_id="template-1", fields=[field])
        use_case = build_remove_use_case(authorization_service, template_repo, uow)

        with pytest.raises(OptionNotFoundError):
            await use_case.execute(
                RemoveFieldOptionCommand(
                    actor_id="admin",
                    template_id="template-1",
                    field_id="field-1",
                    option_id="option-1",
                )
            )
