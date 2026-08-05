import pytest

from app.application.form.dto import PublishFormTemplateCommand
from app.application.form.use_cases.publish_form_template import PublishFormTemplateUseCase
from app.domain.form.entities import FormField
from app.domain.form.enums import FormFieldType, FormTemplateStatus
from app.domain.form.exceptions import FormTemplateHasNoFieldsError


def build_use_case(template_repo, clock, uow, authorization_service) -> PublishFormTemplateUseCase:
    return PublishFormTemplateUseCase(
        template_repo=template_repo,
        clock=clock,
        uow=uow,
        authorization_service=authorization_service,
    )


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
    async def test_publish_with_fields(
        self, template_repo, clock, uow, make_template, authorization_service
    ):
        template = await make_template(template_id="template-1")
        add_field(template)
        authorization_service.grant("admin-1", "form.manage")
        use_case = build_use_case(template_repo, clock, uow, authorization_service)

        result = await use_case.execute(
            PublishFormTemplateCommand(template_id="template-1", published_by="admin-1")
        )

        assert result.status == FormTemplateStatus.PUBLISHED
        assert result.published_at == (await clock.now())
        assert (await template_repo.get_by_id("template-1")).published_by_user_id == "admin-1"
        assert uow.committed is True

    async def test_publish_without_fields_raises(
        self, template_repo, clock, uow, make_template, authorization_service
    ):
        await make_template(template_id="template-1")
        authorization_service.grant("admin-1", "form.manage")
        use_case = build_use_case(template_repo, clock, uow, authorization_service)

        with pytest.raises(FormTemplateHasNoFieldsError):
            await use_case.execute(
                PublishFormTemplateCommand(template_id="template-1", published_by="admin-1")
            )
