from pydantic import BaseModel, Field

from app.domain.form.enums import FormFieldType, FormTemplateStatus


class FormFieldOptionResponse(BaseModel):
    option_id: str
    option_key: str
    label: str
    value: str
    sort_order: int
    is_active: bool


class FormFieldResponse(BaseModel):
    field_id: str
    field_key: str
    label: str
    description: str | None
    field_type: FormFieldType
    is_required: bool
    is_repeatable: bool
    is_unique: bool
    sort_order: int
    validation_rules: dict | None
    is_active: bool
    options: list[FormFieldOptionResponse]


class FormTemplateResponse(BaseModel):
    template_id: str
    category_id: str
    template_key: str
    name: str
    version_no: int
    status: FormTemplateStatus
    is_active: bool
    published_at: str | None
    fields: list[FormFieldResponse]


class CreateFormTemplateRequest(BaseModel):
    category_id: str = Field(..., min_length=1)
    name: str = Field(..., min_length=1)
    template_key: str = Field(..., min_length=1)


class CreateFormTemplateResponse(BaseModel):
    template_id: str
    version_no: int
    status: FormTemplateStatus


class UpdateFormTemplateRequest(BaseModel):
    name: str = Field(..., min_length=1)


class UpdateFormTemplateResponse(BaseModel):
    template_id: str
    name: str


class PublishFormTemplateResponse(BaseModel):
    template_id: str
    status: FormTemplateStatus
    published_at: str


class AddFieldRequest(BaseModel):
    field_key: str = Field(..., min_length=1)
    label: str = Field(..., min_length=1)
    field_type: FormFieldType
    description: str | None = None
    is_required: bool = False
    is_repeatable: bool = False
    is_unique: bool = False
    sort_order: int = 0
    validation_rules: dict | None = None


class AddFieldResponse(BaseModel):
    field_id: str


class UpdateFieldRequest(BaseModel):
    label: str | None = None
    description: str | None = None
    field_type: FormFieldType | None = None
    is_required: bool | None = None
    is_repeatable: bool | None = None
    is_unique: bool | None = None
    sort_order: int | None = None
    validation_rules: dict | None = None
    is_active: bool | None = None


class UpdateFieldResponse(BaseModel):
    field_id: str


class RemoveFieldResponse(BaseModel):
    field_id: str


class AddFieldOptionRequest(BaseModel):
    option_key: str = Field(..., min_length=1)
    label: str = Field(..., min_length=1)
    value: str = Field(..., min_length=1)
    sort_order: int = 0
    is_active: bool = True


class AddFieldOptionResponse(BaseModel):
    option_id: str


class UpdateFieldOptionRequest(BaseModel):
    label: str | None = None
    value: str | None = None
    sort_order: int | None = None
    is_active: bool | None = None


class UpdateFieldOptionResponse(BaseModel):
    option_id: str


class RemoveFieldOptionResponse(BaseModel):
    option_id: str


class DeleteFormTemplateResponse(BaseModel):
    template_id: str


class ListFormTemplateVersionsResponse(BaseModel):
    versions: list[FormTemplateResponse]
