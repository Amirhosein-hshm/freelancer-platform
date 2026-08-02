from datetime import UTC, datetime

import pytest

from app.domain.form.entities import FormField, FormTemplate
from app.domain.form.enums import FormFieldType, FormTemplateStatus
from app.domain.form.exceptions import (
    DuplicateFieldKeyError,
    FieldNotFoundError,
    FormTemplateAlreadyPublishedError,
    FormTemplateHasNoFieldsError,
)
from app.domain.shared.exceptions import InvalidStateTransitionError

NOW = datetime(2026, 8, 2, tzinfo=UTC)


def make_field(**overrides: object) -> FormField:
    fields: dict[str, object] = {
        "id": "field-1",
        "field_key": "title",
        "label": "Title",
        "description": None,
        "field_type": FormFieldType.TEXT,
        "is_required": True,
        "is_repeatable": False,
        "is_unique": False,
        "sort_order": 0,
        "validation_rules": None,
        "is_active": True,
        "created_at": NOW,
    }
    fields.update(overrides)
    return FormField(**fields)  # type: ignore[arg-type]


def make_template(**overrides: object) -> FormTemplate:
    fields: dict[str, object] = {
        "id": "template-1",
        "category_id": "cat-1",
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
    return FormTemplate(**fields)  # type: ignore[arg-type]


class TestAddField:
    def test_add_field_to_draft(self):
        template = make_template()
        field = make_field()
        template.add_field(field)
        assert template.get_field("field-1") == field

    def test_duplicate_field_key_raises(self):
        template = make_template(fields=[make_field()])
        with pytest.raises(DuplicateFieldKeyError):
            template.add_field(make_field())

    def test_add_field_to_published_raises(self):
        template = make_template(status=FormTemplateStatus.PUBLISHED)
        with pytest.raises(InvalidStateTransitionError):
            template.add_field(make_field())


class TestRemoveField:
    def test_remove_field(self):
        template = make_template(fields=[make_field()])
        template.remove_field("field-1")
        assert template.fields == []

    def test_remove_unknown_field_raises(self):
        template = make_template(fields=[make_field()])
        with pytest.raises(FieldNotFoundError):
            template.remove_field("ghost")


class TestPublish:
    def test_publish_draft_with_fields(self):
        template = make_template(fields=[make_field()])
        template.publish("admin-1", NOW)
        assert template.status == FormTemplateStatus.PUBLISHED
        assert template.published_by_user_id == "admin-1"
        assert template.published_at == NOW
        assert template.is_active is True

    def test_publish_without_fields_raises(self):
        template = make_template()
        with pytest.raises(FormTemplateHasNoFieldsError):
            template.publish("admin-1", NOW)

    def test_double_publish_raises(self):
        template = make_template(
            status=FormTemplateStatus.PUBLISHED, fields=[make_field()]
        )
        with pytest.raises(FormTemplateAlreadyPublishedError):
            template.publish("admin-1", NOW)


class TestNewDraftVersion:
    def test_new_draft_copies_fields(self):
        template = make_template(fields=[make_field()])

        draft = template.new_draft_version(2, NOW)

        assert draft.id == "template-1#v2"
        assert draft.version_no == 2
        assert draft.status == FormTemplateStatus.DRAFT
        assert draft.published_at is None
        assert len(draft.fields) == 1
        assert draft.fields[0].field_key == "title"
        assert draft.fields[0].id == "template-1#v2:title"
        assert template.fields[0].id == "field-1"
