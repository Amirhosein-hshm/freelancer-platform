import pytest

from app.application.form.dto import GetFormTemplateQuery
from app.application.form.use_cases.get_form_template import GetFormTemplateUseCase
from app.domain.form.entities import FormField, FormFieldOption
from app.domain.form.enums import FormFieldType, FormTemplateStatus
from app.domain.form.exceptions import FormTemplateNotFoundError


def seed_published(template, field_type=FormFieldType.SELECT) -> None:
    template.fields.append(
        FormField(
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
            options=[
                FormFieldOption(
                    id="opt-1",
                    option_key="backend",
                    label="Backend",
                    value="backend",
                    sort_order=0,
                    is_active=True,
                    created_at=template.created_at,
                )
            ],
            created_at=template.created_at,
        )
    )


class TestGetFormTemplateUseCase:
    async def test_returns_published_template(self, template_repo, make_template):
        template = await make_template(template_id="template-1", status=FormTemplateStatus.PUBLISHED)
        seed_published(template)
        use_case = GetFormTemplateUseCase(template_repo=template_repo)

        result = await use_case.execute(GetFormTemplateQuery(category_id="cat-1"))

        assert result.template_id == "template-1"
        assert result.status == FormTemplateStatus.PUBLISHED
        assert result.fields[0].field_key == "category"
        assert result.fields[0].options[0].option_key == "backend"

    async def test_returns_latest_published_version(self, template_repo, make_template):
        await make_template(
            template_id="template-1",
            category_id="cat-1",
            version_no=1,
            status=FormTemplateStatus.PUBLISHED,
        )
        await make_template(
            template_id="template-2",
            category_id="cat-1",
            version_no=2,
            status=FormTemplateStatus.PUBLISHED,
        )
        use_case = GetFormTemplateUseCase(template_repo=template_repo)

        result = await use_case.execute(GetFormTemplateQuery(category_id="cat-1"))

        assert result.template_id == "template-2"

    async def test_no_published_template_raises(self, template_repo, make_template):
        await make_template(template_id="template-1")
        use_case = GetFormTemplateUseCase(template_repo=template_repo)

        with pytest.raises(FormTemplateNotFoundError):
            await use_case.execute(GetFormTemplateQuery(category_id="cat-1"))
