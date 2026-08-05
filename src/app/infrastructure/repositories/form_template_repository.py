from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.domain.form.entities import FormField, FormTemplate
from app.domain.form.enums import FormTemplateStatus
from app.domain.form.exceptions import FormTemplateNotFoundError
from app.domain.form.repositories import IFormTemplateRepository
from app.domain.shared.types import EntityId
from app.infrastructure.db.models.form_models import (
    FormFieldModel,
    FormFieldOptionModel,
    FormTemplateModel,
)
from app.infrastructure.repositories.form_mapping import to_domain_form_template


class SqlAlchemyFormTemplateRepository(IFormTemplateRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, template: FormTemplate) -> None:
        self._session.add(self._to_model(template))

    async def get_by_id(self, template_id: EntityId) -> FormTemplate:
        row = await self._session.get(
            FormTemplateModel,
            template_id,
            options=[
                selectinload(FormTemplateModel.fields).selectinload(FormFieldModel.options)
            ],
        )
        if row is None:
            raise FormTemplateNotFoundError(f"Form template {template_id} not found.")
        return to_domain_form_template(row)

    async def get_published_for_category(self, category_id: EntityId) -> FormTemplate:
        result = await self._session.execute(
            select(FormTemplateModel)
            .where(
                FormTemplateModel.category_id == category_id,
                FormTemplateModel.status == FormTemplateStatus.PUBLISHED.value,
            )
            .options(
                selectinload(FormTemplateModel.fields).selectinload(FormFieldModel.options)
            )
            .order_by(FormTemplateModel.version_no.desc())
            .limit(1)
        )
        row = result.scalar_one_or_none()
        if row is None:
            raise FormTemplateNotFoundError(
                f"No published form template found for category {category_id}."
            )
        return to_domain_form_template(row)

    async def update(self, template: FormTemplate) -> None:
        row = await self._session.get(
            FormTemplateModel,
            template.id,
            options=[
                selectinload(FormTemplateModel.fields).selectinload(FormFieldModel.options)
            ],
        )
        if row is None:
            raise FormTemplateNotFoundError(f"Form template {template.id} not found.")
        row.category_id = template.category_id
        row.template_key = template.template_key
        row.name = template.name
        row.version_no = template.version_no
        row.status = template.status.value
        row.is_active = template.is_active
        row.published_by_user_id = template.published_by_user_id
        row.published_at = template.published_at
        row.deleted_at = template.deleted_at
        row.fields = [self._to_field_model(field) for field in template.fields]

    async def list_versions(self, category_id: EntityId) -> list[FormTemplate]:
        result = await self._session.execute(
            select(FormTemplateModel)
            .where(FormTemplateModel.category_id == category_id)
            .options(
                selectinload(FormTemplateModel.fields).selectinload(FormFieldModel.options)
            )
            .order_by(FormTemplateModel.version_no.desc())
        )
        return [to_domain_form_template(row) for row in result.scalars().all()]

    def _to_model(self, template: FormTemplate) -> FormTemplateModel:
        return FormTemplateModel(
            id=template.id,
            category_id=template.category_id,
            template_key=template.template_key,
            name=template.name,
            version_no=template.version_no,
            status=template.status.value,
            is_active=template.is_active,
            published_by_user_id=template.published_by_user_id,
            published_at=template.published_at,
            deleted_at=template.deleted_at,
            fields=[self._to_field_model(field) for field in template.fields],
        )

    def _to_field_model(self, field: FormField) -> FormFieldModel:
        return FormFieldModel(
            id=field.id,
            field_key=field.field_key,
            label=field.label,
            description=field.description,
            field_type=field.field_type.value,
            is_required=field.is_required,
            is_repeatable=field.is_repeatable,
            is_unique=field.is_unique,
            sort_order=field.sort_order,
            validation_rules=field.validation_rules,
            is_active=field.is_active,
            options=[
                FormFieldOptionModel(
                    id=option.id,
                    option_key=option.option_key,
                    label=option.label,
                    value=option.value,
                    sort_order=option.sort_order,
                    is_active=option.is_active,
                )
                for option in field.options
            ],
        )
