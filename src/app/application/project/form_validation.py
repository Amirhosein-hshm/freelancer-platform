from datetime import date, datetime
from decimal import Decimal, InvalidOperation

from app.application.project.dto import FormValueInput
from app.application.shared.exceptions import FormValidationError
from app.domain.form.entities import FormTemplate
from app.domain.form.enums import FormFieldType

_BOOLEAN_TRUE = {"true", "1", "yes", "on"}
_BOOLEAN_FALSE = {"false", "0", "no", "off"}


def validate_form_values(
    template: FormTemplate, form_values: list[FormValueInput]
) -> None:
    """Validate submitted form values against a published form template.

    Raises :class:`FormValidationError` (application-level) on any violation.
    """
    fields_by_id = {field.id: field for field in template.fields}
    provided_by_id: dict[str, FormValueInput] = {
        value.field_id: value for value in form_values
    }
    for submitted in form_values:
        if submitted.field_id not in fields_by_id:
            raise FormValidationError(
                f"Unknown field_id '{submitted.field_id}' in submitted form values."
            )
    for field in template.fields:
        value = provided_by_id.get(field.id)
        if field.is_required and (value is None or not value.value.strip()):
            raise FormValidationError(
                f"Field '{field.label}' is required but no value was provided."
            )
        if value is None or not value.value.strip():
            continue
        _validate_value(field.field_type, field.label, value.value)


def _validate_value(field_type: FormFieldType, label: str, raw: str) -> None:
    value = raw.strip()
    if field_type == FormFieldType.NUMBER:
        if not value.lstrip("-").isdigit():
            raise FormValidationError(f"Field '{label}' must be a whole number.")
    elif field_type == FormFieldType.DECIMAL:
        try:
            Decimal(value)
        except InvalidOperation:
            raise FormValidationError(f"Field '{label}' must be a decimal number.") from None
    elif field_type == FormFieldType.BOOLEAN:
        if value.lower() not in _BOOLEAN_TRUE | _BOOLEAN_FALSE:
            raise FormValidationError(
                f"Field '{label}' must be true or false."
            )
    elif field_type == FormFieldType.DATE:
        try:
            date.fromisoformat(value)
        except ValueError:
            raise FormValidationError(
                f"Field '{label}' must be a valid date (YYYY-MM-DD)."
            ) from None
    elif field_type == FormFieldType.DATETIME:
        try:
            datetime.fromisoformat(value)
        except ValueError:
            raise FormValidationError(
                f"Field '{label}' must be a valid datetime (ISO 8601)."
            ) from None
    elif field_type == FormFieldType.EMAIL:
        if "@" not in value or "." not in value.split("@")[-1]:
            raise FormValidationError(f"Field '{label}' must be a valid email address.")
    elif field_type == FormFieldType.URL and not value.lower().startswith(("http://", "https://")):
        raise FormValidationError(f"Field '{label}' must be a valid URL.")
