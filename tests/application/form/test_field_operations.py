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
    def test_add_field_succeeds(self, template_repo, id_generator, clock, uow, make_template):
        make_template(template_id="template-1")
        use_case = AddFieldUseCase(
            template_repo=template_repo, id_generator=id_generator, clock=clock, uow=uow
        )

        result = use_case.execute(
            AddFieldCommand(
                template_id="template-1",
                field_key="budget",
                label="Budget",
                field_type=FormFieldType.DECIMAL,
                is_required=True,
            )
        )

        template = template_repo.get_by_id("template-1")
        field = template.get_field(result.field_id)
        assert field.field_key == "budget"
        assert field.field_type == FormFieldType.DECIMAL
        assert field.is_required is True
        assert uow.committed is True

    def test_duplicate_field_key_raises(
        self, template_repo, id_generator, clock, uow, make_template
    ):
        template = make_template(template_id="template-1")
        seed_field(template, field_type=FormFieldType.TEXT)
        use_case = AddFieldUseCase(
            template_repo=template_repo, id_generator=id_generator, clock=clock, uow=uow
        )

        with pytest.raises(DuplicateFieldKeyError):
            use_case.execute(
                AddFieldCommand(
                    template_id="template-1",
                    field_key="category",
                    label="Category",
                    field_type=FormFieldType.TEXT,
                )
            )

    def test_add_field_to_published_raises(
        self, template_repo, id_generator, clock, uow, make_template
    ):
        make_template(template_id="template-1", status=FormTemplateStatus.PUBLISHED)
        use_case = AddFieldUseCase(
            template_repo=template_repo, id_generator=id_generator, clock=clock, uow=uow
        )

        with pytest.raises(InvalidStateTransitionError):
            use_case.execute(
                AddFieldCommand(
                    template_id="template-1",
                    field_key="budget",
                    label="Budget",
                    field_type=FormFieldType.DECIMAL,
                )
            )


class TestUpdateFieldUseCase:
    def test_update_field_succeeds(self, template_repo, make_template):
        template = make_template(template_id="template-1")
        seed_field(template)
        use_case = UpdateFieldUseCase(template_repo=template_repo)

        result = use_case.execute(
            UpdateFieldCommand(
                template_id="template-1",
                field_id="field-1",
                label="Project Category",
                is_required=False,
            )
        )

        assert result.field_id == "field-1"
        field = template_repo.get_by_id("template-1").get_field("field-1")
        assert field.label == "Project Category"
        assert field.is_required is False

    def test_update_field_type_clears_options(self, template_repo, make_template):
        template = make_template(template_id="template-1")
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
        use_case = UpdateFieldUseCase(template_repo=template_repo)

        use_case.execute(
            UpdateFieldCommand(template_id="template-1", field_id="field-1", field_type=FormFieldType.TEXT)
        )

        assert template_repo.get_by_id("template-1").get_field("field-1").options == []

    def test_update_all_attributes(self, template_repo, make_template):
        template = make_template(template_id="template-1")
        seed_field(template)
        use_case = UpdateFieldUseCase(template_repo=template_repo)

        use_case.execute(
            UpdateFieldCommand(
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

        field = template_repo.get_by_id("template-1").get_field("field-1")
        assert field.description == "Pick a category"
        assert field.field_type == FormFieldType.TEXT
        assert field.is_repeatable is True
        assert field.is_unique is True
        assert field.sort_order == 5
        assert field.validation_rules == {"min_length": 3}
        assert field.is_active is False

    def test_update_unknown_field_raises(self, template_repo, make_template):
        make_template(template_id="template-1")
        use_case = UpdateFieldUseCase(template_repo=template_repo)

        with pytest.raises(FieldNotFoundError):
            use_case.execute(
                UpdateFieldCommand(template_id="template-1", field_id="ghost", label="X")
            )


class TestRemoveFieldUseCase:
    def test_remove_field_succeeds(self, template_repo, uow, make_template):
        template = make_template(template_id="template-1")
        seed_field(template, field_type=FormFieldType.TEXT)
        use_case = RemoveFieldUseCase(template_repo=template_repo, uow=uow)

        result = use_case.execute(RemoveFieldCommand(template_id="template-1", field_id="field-1"))

        assert result.field_id == "field-1"
        assert template_repo.get_by_id("template-1").fields == []
        assert uow.committed is True


class TestAddFieldOptionUseCase:
    def test_add_option_to_select_field(self, template_repo, id_generator, clock, uow, make_template):
        template = make_template(template_id="template-1")
        seed_field(template)
        use_case = AddFieldOptionUseCase(
            template_repo=template_repo, id_generator=id_generator, clock=clock, uow=uow
        )

        result = use_case.execute(
            AddFieldOptionCommand(
                template_id="template-1",
                field_id="field-1",
                option_key="backend",
                label="Backend",
                value="backend",
            )
        )

        field = template_repo.get_by_id("template-1").get_field("field-1")
        assert field.get_option("backend").id == result.option_id
        assert uow.committed is True

    def test_add_option_to_text_field_raises(
        self, template_repo, id_generator, clock, uow, make_template
    ):
        template = make_template(template_id="template-1")
        seed_field(template, field_type=FormFieldType.TEXT)
        use_case = AddFieldOptionUseCase(
            template_repo=template_repo, id_generator=id_generator, clock=clock, uow=uow
        )

        with pytest.raises(InvalidFieldOptionError):
            use_case.execute(
                AddFieldOptionCommand(
                    template_id="template-1",
                    field_id="field-1",
                    option_key="backend",
                    label="Backend",
                    value="backend",
                )
            )
