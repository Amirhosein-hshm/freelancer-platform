from datetime import UTC, datetime

import pytest

from app.domain.form.entities import FormField, FormFieldOption
from app.domain.form.enums import FormFieldType
from app.domain.form.exceptions import DuplicateOptionKeyError, InvalidFieldOptionError

NOW = datetime(2026, 8, 2, tzinfo=UTC)


def make_option(**overrides: object) -> FormFieldOption:
    fields: dict[str, object] = {
        "id": "option-1",
        "option_key": "opt_a",
        "label": "Option A",
        "value": "a",
        "sort_order": 0,
        "is_active": True,
        "created_at": NOW,
    }
    fields.update(overrides)
    return FormFieldOption(**fields)  # type: ignore[arg-type]


def make_field(field_type: FormFieldType = FormFieldType.SELECT) -> FormField:
    return FormField(
        id="field-1",
        field_key="category",
        label="Category",
        description=None,
        field_type=field_type,
        is_required=True,
        is_repeatable=False,
        is_unique=False,
        sort_order=0,
        validation_rules=None,
        created_at=NOW,
    )


class TestAddOption:
    def test_add_option_to_select_field(self):
        field = make_field(FormFieldType.SELECT)
        option = make_option()
        field.add_option(option)
        assert field.get_option("opt_a") == option

    def test_add_option_to_text_field_raises(self):
        field = make_field(FormFieldType.TEXT)
        with pytest.raises(InvalidFieldOptionError):
            field.add_option(make_option())

    def test_duplicate_option_key_raises(self):
        field = make_field(FormFieldType.SELECT)
        field.add_option(make_option())
        with pytest.raises(DuplicateOptionKeyError):
            field.add_option(make_option())


class TestChangeType:
    def test_change_type_clears_options(self):
        field = make_field(FormFieldType.SELECT)
        field.add_option(make_option())
        field.change_type(FormFieldType.TEXT)
        assert field.field_type == FormFieldType.TEXT
        assert field.options == []

    def test_change_type_to_select_keeps_options(self):
        field = make_field(FormFieldType.TEXT)
        field.change_type(FormFieldType.SELECT)
        assert field.field_type == FormFieldType.SELECT
