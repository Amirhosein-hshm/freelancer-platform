import pytest

from app.application.form.dto import (
    AddFieldCommand,
    AddFieldOptionCommand,
    RemoveFieldCommand,
    UpdateFieldCommand,
)
from app.application.form.use_cases.add_field import AddFieldUseCase
from app.application.form.use_cases.add_field_option import AddFieldOptionUseCase
from app.application.form.use_cases.remove_field import RemoveFieldUseCase
from app.application.form.use_cases.update_field import UpdateFieldUseCase
from app.domain.form.entities import FormField, FormFieldOption
from app.domain.form.enums import FormFieldType, FormTemplateStatus
from app.domain.form.exceptions import (
    DuplicateFieldKeyError,
    FieldNotFoundError,
    InvalidFieldOptionError,
)
from app.domain.shared.exceptions import InvalidStateTransitionError


def seed_field(template, field_id: str = "field-1", field_type=FormFieldType.SELECT) -> None:
    template.fields.append(
        FormField(
            id=field_id,
            field_key="category",
            label="Category",
            description=None,
            field_type=field_type,
            is_required=True,
            is_repeatable=False,
            is_unique=False,
            sort_order=0,
            validation_rules=None,
            created_at=template.created_at,
        )
    )


class TestAddFieldUseCase:
    async def test_add_field_succeeds(
        self, template_repo, id_generator, clock, uow, make_template, authorization_service
    ):
        await make_template(template_id="template-1")
        authorization_service.grant("admin", "form.manage")
        use_case = AddFieldUseCase(
            authorization_service=authorization_service,
            template_repo=template_repo,
            id_generator=id_generator,
            clock=clock,
            uow=uow,
        )

        result = await use_case.execute(
            AddFieldCommand(
                actor_id="admin",
                template_id="template-1",
                field_key="budget",
                label="Budget",
                field_type=FormFieldType.DECIMAL,
                is_required=True,
            )
        )

        template = await template_repo.get_by_id("template-1")
        field = template.get_field(result.field_id)
        assert field.field_key == "budget"
        assert field.field_type == FormFieldType.DECIMAL
        assert field.is_required is True
        assert uow.committed is True

    async def test_duplicate_field_key_raises(
        self, template_repo, id_generator, clock, uow, make_template, authorization_service
    ):
        template = await make_template(template_id="template-1")
        seed_field(template, field_type=FormFieldType.TEXT)
        authorization_service.grant("admin", "form.manage")
        use_case = AddFieldUseCase(
            authorization_service=authorization_service,
            template_repo=template_repo,
            id_generator=id_generator,
            clock=clock,
            uow=uow,
        )

        with pytest.raises(DuplicateFieldKeyError):
            await use_case.execute(
                AddFieldCommand(
                    actor_id="admin",
                    template_id="template-1",
                    field_key="category",
                    label="Category",
                    field_type=FormFieldType.TEXT,
                )
            )

    async def test_add_field_to_published_raises(
        self, template_repo, id_generator, clock, uow, make_template, authorization_service
    ):
        await make_template(template_id="template-1", status=FormTemplateStatus.PUBLISHED)
        authorization_service.grant("admin", "form.manage")
        use_case = AddFieldUseCase(
            authorization_service=authorization_service,
            template_repo=template_repo,
            id_generator=id_generator,
            clock=clock,
            uow=uow,
        )

        with pytest.raises(InvalidStateTransitionError):
            await use_case.execute(
                AddFieldCommand(
                    actor_id="admin",
                    template_id="template-1",
                    field_key="budget",
                    label="Budget",
                    field_type=FormFieldType.DECIMAL,
                )
            )


class TestUpdateFieldUseCase:
    async def test_update_field_succeeds(self, template_repo, make_template, authorization_service):
        template = await make_template(template_id="template-1")
        seed_field(template)
        authorization_service.grant("admin", "form.manage")
        use_case = UpdateFieldUseCase(
            template_repo=template_repo, authorization_service=authorization_service
        )

        result = await use_case.execute(
            UpdateFieldCommand(
                actor_id="admin",
                template_id="template-1",
                field_id="field-1",
                label="Project Category",
                is_required=False,
            )
        )

        assert result.field_id == "field-1"
        field = (await template_repo.get_by_id("template-1")).get_field("field-1")
        assert field.label == "Project Category"
        assert field.is_required is False

    async def test_update_field_type_clears_options(
        self, template_repo, make_template, authorization_service
    ):
        template = await make_template(template_id="template-1")
        seed_field(template)
        template.get_field("field-1").add_option(
            FormFieldOption(
                id="opt-1",
                option_key="a",
                label="A",
                value="a",
                sort_order=0,
                is_active=True,
                created_at=template.created_at,
            )
        )
        authorization_service.grant("admin", "form.manage")
        use_case = UpdateFieldUseCase(
            template_repo=template_repo, authorization_service=authorization_service
        )

        await use_case.execute(
            UpdateFieldCommand(
                actor_id="admin",
                template_id="template-1",
                field_id="field-1",
                field_type=FormFieldType.TEXT,
            )
        )

        assert (await template_repo.get_by_id("template-1")).get_field("field-1").options == []

    async def test_update_all_attributes(self, template_repo, make_template, authorization_service):
        template = await make_template(template_id="template-1")
        seed_field(template)
        authorization_service.grant("admin", "form.manage")
        use_case = UpdateFieldUseCase(
            template_repo=template_repo, authorization_service=authorization_service
        )

        await use_case.execute(
            UpdateFieldCommand(
                actor_id="admin",
                template_id="template-1",
                field_id="field-1",
                description="Pick a category",
                field_type=FormFieldType.TEXT,
                is_repeatable=True,
                is_unique=True,
                sort_order=5,
                validation_rules={"min_length": 3},
                is_active=False,
            )
        )

        field = (await template_repo.get_by_id("template-1")).get_field("field-1")
        assert field.description == "Pick a category"
        assert field.field_type == FormFieldType.TEXT
        assert field.is_repeatable is True
        assert field.is_unique is True
        assert field.sort_order == 5
        assert field.validation_rules == {"min_length": 3}
        assert field.is_active is False

    async def test_update_unknown_field_raises(self, template_repo, make_template, authorization_service):
        await make_template(template_id="template-1")
        authorization_service.grant("admin", "form.manage")
        use_case = UpdateFieldUseCase(
            template_repo=template_repo, authorization_service=authorization_service
        )

        with pytest.raises(FieldNotFoundError):
            await use_case.execute(
                UpdateFieldCommand(
                    actor_id="admin", template_id="template-1", field_id="ghost", label="X"
                )
            )


class TestRemoveFieldUseCase:
    async def test_remove_field_succeeds(
        self, template_repo, uow, make_template, authorization_service
    ):
        template = await make_template(template_id="template-1")
        seed_field(template, field_type=FormFieldType.TEXT)
        authorization_service.grant("admin", "form.manage")
        use_case = RemoveFieldUseCase(
            template_repo=template_repo, uow=uow, authorization_service=authorization_service
        )

        result = await use_case.execute(
            RemoveFieldCommand(actor_id="admin", template_id="template-1", field_id="field-1")
        )

        assert result.field_id == "field-1"
        assert (await template_repo.get_by_id("template-1")).fields == []
        assert uow.committed is True


class TestAddFieldOptionUseCase:
    async def test_add_option_to_select_field(
        self, template_repo, id_generator, clock, uow, make_template, authorization_service
    ):
        template = await make_template(template_id="template-1")
        seed_field(template)
        authorization_service.grant("admin", "form.manage")
        use_case = AddFieldOptionUseCase(
            authorization_service=authorization_service,
            template_repo=template_repo,
            id_generator=id_generator,
            clock=clock,
            uow=uow,
        )

        result = await use_case.execute(
            AddFieldOptionCommand(
                actor_id="admin",
                template_id="template-1",
                field_id="field-1",
                option_key="backend",
                label="Backend",
                value="backend",
            )
        )

        field = (await template_repo.get_by_id("template-1")).get_field("field-1")
        assert field.get_option("backend").id == result.option_id
        assert uow.committed is True

    async def test_add_option_to_text_field_raises(
        self, template_repo, id_generator, clock, uow, make_template, authorization_service
    ):
        template = await make_template(template_id="template-1")
        seed_field(template, field_type=FormFieldType.TEXT)
        authorization_service.grant("admin", "form.manage")
        use_case = AddFieldOptionUseCase(
            authorization_service=authorization_service,
            template_repo=template_repo,
            id_generator=id_generator,
            clock=clock,
            uow=uow,
        )

        with pytest.raises(InvalidFieldOptionError):
            await use_case.execute(
                AddFieldOptionCommand(
                    actor_id="admin",
                    template_id="template-1",
                    field_id="field-1",
                    option_key="backend",
                    label="Backend",
                    value="backend",
                )
            )
