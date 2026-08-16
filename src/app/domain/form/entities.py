from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from app.domain.form.enums import FormFieldType, FormTemplateStatus
from app.domain.form.exceptions import (
    DuplicateFieldKeyError,
    DuplicateOptionKeyError,
    FieldNotFoundError,
    FormTemplateAlreadyPublishedError,
    FormTemplateHasNoFieldsError,
    InvalidFieldOptionError,
    OptionNotFoundError,
)
from app.domain.shared.entity import AggregateRoot, Entity
from app.domain.shared.exceptions import InvalidStateTransitionError
from app.domain.shared.types import EntityId

SELECT_TYPES = (FormFieldType.SELECT, FormFieldType.MULTI_SELECT)


@dataclass(eq=False)
class FormFieldOption(Entity):
    option_key: str
    label: str
    value: str
    sort_order: int
    is_active: bool


@dataclass(eq=False)
class FormField(Entity):
    field_key: str
    label: str
    description: str | None
    field_type: FormFieldType
    is_required: bool
    is_repeatable: bool
    is_unique: bool
    sort_order: int
    validation_rules: dict[str, Any] | None
    options: list[FormFieldOption] = field(default_factory=list)
    is_active: bool = True

    def add_option(self, option: FormFieldOption) -> None:
        if self.field_type not in SELECT_TYPES:
            raise InvalidFieldOptionError(
                f"Field '{self.field_key}' is '{self.field_type.value}'; options are only "
                "allowed for SELECT and MULTI_SELECT fields."
            )
        if any(o.option_key == option.option_key for o in self.options):
            raise DuplicateOptionKeyError(f"Option '{option.option_key}' already exists on field '{self.field_key}'.")
        self.options.append(option)

    def change_type(self, new_type: FormFieldType) -> None:
        self.field_type = new_type
        if new_type not in SELECT_TYPES:
            self.options = []

    def get_option(self, option_key: str) -> FormFieldOption | None:
        return next((o for o in self.options if o.option_key == option_key), None)

    def _find_option_index(self, option_id: EntityId) -> int:
        for i, option in enumerate(self.options):
            if option.id == option_id:
                return i
        raise OptionNotFoundError(f"Option {option_id} not found on field {self.field_key}.")

    def update_option(
        self,
        option_id: EntityId,
        label: str | None = None,
        value: str | None = None,
        sort_order: int | None = None,
        is_active: bool | None = None,
    ) -> None:
        index = self._find_option_index(option_id)
        option = self.options[index]
        if label is not None:
            option.label = label
        if value is not None:
            option.value = value
        if sort_order is not None:
            option.sort_order = sort_order
        if is_active is not None:
            option.is_active = is_active

    def remove_option(self, option_id: EntityId) -> None:
        index = self._find_option_index(option_id)
        self.options.pop(index)


@dataclass(eq=False)
class FormTemplate(AggregateRoot):
    category_id: EntityId
    template_key: str
    name: str
    version_no: int
    status: FormTemplateStatus
    is_active: bool
    published_by_user_id: EntityId | None
    published_at: datetime | None
    fields: list[FormField] = field(default_factory=list)
    deleted_at: datetime | None = None

    def add_field(self, field: FormField) -> None:
        self.require_draft("add fields")
        if any(f.field_key == field.field_key for f in self.fields):
            raise DuplicateFieldKeyError(f"Field key '{field.field_key}' already exists in template {self.id}.")
        self.fields.append(field)

    def remove_field(self, field_id: EntityId) -> None:
        self.require_draft("remove fields")
        for i, existing in enumerate(self.fields):
            if existing.id == field_id:
                self.fields.pop(i)
                return
        raise FieldNotFoundError(f"Field {field_id} not found in template {self.id}.")

    def get_field(self, field_id: EntityId) -> FormField:
        for existing in self.fields:
            if existing.id == field_id:
                return existing
        raise FieldNotFoundError(f"Field {field_id} not found in template {self.id}.")

    def publish(self, published_by: EntityId, at: datetime) -> None:
        if not self.fields:
            raise FormTemplateHasNoFieldsError(f"Template {self.id} has no fields and cannot be published.")
        if self.status == FormTemplateStatus.PUBLISHED:
            raise FormTemplateAlreadyPublishedError(f"Template {self.id} is already published.")
        if self.status == FormTemplateStatus.ARCHIVED:
            raise InvalidStateTransitionError(f"Cannot publish archived template {self.id}.")
        self.status = FormTemplateStatus.PUBLISHED
        self.published_by_user_id = published_by
        self.published_at = at
        self.is_active = True

    def new_draft_version(self, new_version_no: int, at: datetime) -> "FormTemplate":
        new_template_id = f"{self.id}#v{new_version_no}"
        copied_fields = [
            FormField(
                id=f"{new_template_id}:{f.field_key}",
                field_key=f.field_key,
                label=f.label,
                description=f.description,
                field_type=f.field_type,
                is_required=f.is_required,
                is_repeatable=f.is_repeatable,
                is_unique=f.is_unique,
                sort_order=f.sort_order,
                validation_rules=f.validation_rules,
                options=list(f.options),
                is_active=f.is_active,
                created_at=at,
            )
            for f in self.fields
        ]
        return FormTemplate(
            id=new_template_id,
            category_id=self.category_id,
            template_key=self.template_key,
            name=self.name,
            version_no=new_version_no,
            status=FormTemplateStatus.DRAFT,
            is_active=True,
            published_by_user_id=None,
            published_at=None,
            fields=copied_fields,
            deleted_at=None,
            created_at=at,
        )

    def require_draft(self, action: str) -> None:
        if self.status != FormTemplateStatus.DRAFT:
            raise InvalidStateTransitionError(f"Template {self.id} is '{self.status.value}' and cannot {action}.")
