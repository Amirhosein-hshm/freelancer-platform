import pytest

from app.application.form.dto import PublishFormTemplateCommand
from app.application.form.use_cases.publish_form_template import PublishFormTemplateUseCase
from app.domain.form.entities import FormField
from app.domain.form.enums import FormFieldType, FormTemplateStatus
from app.domain.form.exceptions import FormTemplateHasNoFieldsError


def build_use_case(template_repo, clock, uow) -> PublishFormTemplateUseCase:
    return PublishFormTemplateUseCase(template_repo=template_repo, clock=clock, uow=uow)


def add_field(template) -> None:
    template.fields.append(
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
            created_at=template.created_at,
        )
    )


class TestPublishFormTemplateUseCase:
    def test_publish_with_fields(self, template_repo, clock, uow, make_template):
        template = make_template(template_id="template-1")
        add_field(template)
        use_case = build_use_case(template_repo, clock, uow)

        result = use_case.execute(
            PublishFormTemplateCommand(template_id="template-1", published_by="admin-1")
        )

        assert result.status == FormTemplateStatus.PUBLISHED
        assert result.published_at == clock.now()
        assert template_repo.get_by_id("template-1").published_by_user_id == "admin-1"
        assert uow.committed is True

    def test_publish_without_fields_raises(self, template_repo, clock, uow, make_template):
        make_template(template_id="template-1")
        use_case = build_use_case(template_repo, clock, uow)

        with pytest.raises(FormTemplateHasNoFieldsError):
            use_case.execute(
                PublishFormTemplateCommand(template_id="template-1", published_by="admin-1")
            )
