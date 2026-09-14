from dataclasses import dataclass
from datetime import datetime
from typing import Any

from app.application.shared.exceptions import ValidationError
from app.domain.form.enums import FormFieldType, FormTemplateStatus
from app.domain.shared.types import EntityId


@dataclass(frozen=True)
class FormFieldOptionResult:
    option_id: EntityId
    option_key: str
    label: str
    value: str
    sort_order: int
    is_active: bool


@dataclass(frozen=True)
class FormFieldResult:
    field_id: EntityId
    field_key: str
    label: str
    description: str | None
    field_type: FormFieldType
    is_required: bool
    is_repeatable: bool
    is_unique: bool
    sort_order: int
    validation_rules: dict[str, Any] | None
    is_active: bool
    options: list[FormFieldOptionResult]


@dataclass(frozen=True)
class FormTemplateResult:
    template_id: EntityId
    category_id: EntityId
    template_key: str
    name: str
    version_no: int
    status: FormTemplateStatus
    is_active: bool
    published_at: datetime | None
    fields: list[FormFieldResult]


@dataclass(frozen=True)
class CreateFormTemplateCommand:
    actor_id: EntityId
    category_id: EntityId
    name: str
    template_key: str

    def validate(self) -> None:
        if not self.name.strip() or not self.template_key.strip():
            raise ValidationError("name and template_key are required.")


@dataclass(frozen=True)
class CreateFormTemplateResult:
    template_id: EntityId
    version_no: int
    status: FormTemplateStatus


@dataclass(frozen=True)
class UpdateFormTemplateCommand:
    actor_id: EntityId
    template_id: EntityId
    name: str

    def validate(self) -> None:
        if not self.name.strip():
            raise ValidationError("name is required.")


@dataclass(frozen=True)
class UpdateFormTemplateResult:
    template_id: EntityId
    name: str


@dataclass(frozen=True)
class PublishFormTemplateCommand:
    template_id: EntityId
    published_by: EntityId


@dataclass(frozen=True)
class PublishFormTemplateResult:
    template_id: EntityId
    status: FormTemplateStatus
    published_at: datetime


@dataclass(frozen=True)
class AddFieldCommand:
    actor_id: EntityId
    template_id: EntityId
    field_key: str
    label: str
    field_type: FormFieldType
    description: str | None = None
    is_required: bool = False
    is_repeatable: bool = False
    is_unique: bool = False
    sort_order: int = 0
    validation_rules: dict[str, Any] | None = None

    def validate(self) -> None:
        if not self.field_key.strip() or not self.label.strip():
            raise ValidationError("field_key and label are required.")


@dataclass(frozen=True)
class AddFieldResult:
    field_id: EntityId


@dataclass(frozen=True)
class UpdateFieldCommand:
    actor_id: EntityId
    template_id: EntityId
    field_id: EntityId
    label: str | None = None
    description: str | None = None
    field_type: FormFieldType | None = None
    is_required: bool | None = None
    is_repeatable: bool | None = None
    is_unique: bool | None = None
    sort_order: int | None = None
    validation_rules: dict[str, Any] | None = None
    is_active: bool | None = None

    def validate(self) -> None:
        if self.label is not None and not self.label.strip():
            raise ValidationError("label cannot be empty.")


@dataclass(frozen=True)
class UpdateFieldResult:
    field_id: EntityId


@dataclass(frozen=True)
class RemoveFieldCommand:
    actor_id: EntityId
    template_id: EntityId
    field_id: EntityId


@dataclass(frozen=True)
class RemoveFieldResult:
    field_id: EntityId


@dataclass(frozen=True)
class AddFieldOptionCommand:
    actor_id: EntityId
    template_id: EntityId
    field_id: EntityId
    option_key: str
    label: str
    value: str
    sort_order: int = 0
    is_active: bool = True

    def validate(self) -> None:
        if not self.option_key.strip() or not self.label.strip():
            raise ValidationError("option_key and label are required.")


@dataclass(frozen=True)
class AddFieldOptionResult:
    option_id: EntityId


@dataclass(frozen=True)
class UpdateFieldOptionCommand:
    actor_id: EntityId
    template_id: EntityId
    field_id: EntityId
    option_id: EntityId
    label: str | None = None
    value: str | None = None
    sort_order: int | None = None
    is_active: bool | None = None

    def validate(self) -> None:
        if self.label is not None and not self.label.strip():
            raise ValidationError("label cannot be empty.")
        if self.value is not None and not self.value.strip():
            raise ValidationError("value cannot be empty.")


@dataclass(frozen=True)
class UpdateFieldOptionResult:
    option_id: EntityId


@dataclass(frozen=True)
class RemoveFieldOptionCommand:
    actor_id: EntityId
    template_id: EntityId
    field_id: EntityId
    option_id: EntityId


@dataclass(frozen=True)
class RemoveFieldOptionResult:
    option_id: EntityId


@dataclass(frozen=True)
class DeleteFormTemplateCommand:
    actor_id: EntityId
    template_id: EntityId


@dataclass(frozen=True)
class DeleteFormTemplateResult:
    template_id: EntityId


@dataclass(frozen=True)
class GetFormTemplateQuery:
    category_id: EntityId
