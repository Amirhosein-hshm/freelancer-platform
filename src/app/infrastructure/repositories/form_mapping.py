from app.domain.form.entities import FormField, FormFieldOption, FormTemplate
from app.domain.form.enums import FormFieldType, FormTemplateStatus


def to_domain_form_template(row: object) -> FormTemplate:
    return FormTemplate(
        id=row.id,
        created_at=row.created_at,
        updated_at=row.updated_at,
        category_id=row.category_id,
        template_key=row.template_key,
        name=row.name,
        version_no=row.version_no,
        status=FormTemplateStatus(row.status),
        is_active=row.is_active,
        published_by_user_id=row.published_by_user_id,
        published_at=row.published_at,
        fields=[to_domain_form_field(field) for field in row.fields],
        deleted_at=row.deleted_at,
    )


def to_domain_form_field(row: object) -> FormField:
    return FormField(
        id=row.id,
        created_at=row.created_at,
        updated_at=row.updated_at,
        field_key=row.field_key,
        label=row.label,
        description=row.description,
        field_type=FormFieldType(row.field_type),
        is_required=row.is_required,
        is_repeatable=row.is_repeatable,
        is_unique=row.is_unique,
        sort_order=row.sort_order,
        validation_rules=row.validation_rules,
        options=[to_domain_form_field_option(option) for option in row.options],
        is_active=row.is_active,
    )


def to_domain_form_field_option(row: object) -> FormFieldOption:
    return FormFieldOption(
        id=row.id,
        created_at=row.created_at,
        updated_at=row.updated_at,
        option_key=row.option_key,
        label=row.label,
        value=row.value,
        sort_order=row.sort_order,
        is_active=row.is_active,
    )
