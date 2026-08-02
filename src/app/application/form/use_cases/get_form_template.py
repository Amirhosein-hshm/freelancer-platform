from app.application.form.dto import (
    FormFieldOptionResult,
    FormFieldResult,
    FormTemplateResult,
    GetFormTemplateQuery,
)
from app.application.shared.use_case import UseCase
from app.domain.form.entities import FormField, FormFieldOption, FormTemplate
from app.domain.form.repositories import IFormTemplateRepository


def to_template_result(template: FormTemplate) -> FormTemplateResult:
    return FormTemplateResult(
        template_id=template.id,
        category_id=template.category_id,
        template_key=template.template_key,
        name=template.name,
        version_no=template.version_no,
        status=template.status,
        is_active=template.is_active,
        published_at=template.published_at,
        fields=[_to_field_result(f) for f in template.fields],
    )


def _to_field_result(field: FormField) -> FormFieldResult:
    return FormFieldResult(
        field_id=field.id,
        field_key=field.field_key,
        label=field.label,
        description=field.description,
        field_type=field.field_type,
        is_required=field.is_required,
        is_repeatable=field.is_repeatable,
        is_unique=field.is_unique,
        sort_order=field.sort_order,
        validation_rules=field.validation_rules,
        is_active=field.is_active,
        options=[_to_option_result(o) for o in field.options],
    )


def _to_option_result(option: FormFieldOption) -> FormFieldOptionResult:
    return FormFieldOptionResult(
        option_id=option.id,
        option_key=option.option_key,
        label=option.label,
        value=option.value,
        sort_order=option.sort_order,
        is_active=option.is_active,
    )


class GetFormTemplateUseCase(UseCase[GetFormTemplateQuery, FormTemplateResult]):
    def __init__(self, template_repo: IFormTemplateRepository) -> None:
        self._template_repo = template_repo

    def execute(self, request: GetFormTemplateQuery) -> FormTemplateResult:
        template = self._template_repo.get_published_for_category(request.category_id)
        return to_template_result(template)
