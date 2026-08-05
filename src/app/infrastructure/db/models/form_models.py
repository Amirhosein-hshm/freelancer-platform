from datetime import datetime

from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.db.base import Base, TimestampMixin


class FormTemplateModel(TimestampMixin, Base):
    __tablename__ = "form_templates"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    category_id: Mapped[str] = mapped_column(ForeignKey("categories.id"), index=True, nullable=False)
    template_key: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    version_no: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False)
    published_by_user_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    fields: Mapped[list["FormFieldModel"]] = relationship(
        back_populates="form_template",
        cascade="all, delete-orphan",
        order_by="FormFieldModel.sort_order",
    )


class FormFieldModel(TimestampMixin, Base):
    __tablename__ = "form_fields"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    form_template_id: Mapped[str] = mapped_column(
        ForeignKey("form_templates.id"), index=True, nullable=False
    )
    field_key: Mapped[str] = mapped_column(String(50), nullable=False)
    label: Mapped[str] = mapped_column(String(120), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    field_type: Mapped[str] = mapped_column(String(20), nullable=False)
    is_required: Mapped[bool] = mapped_column(Boolean, nullable=False)
    is_repeatable: Mapped[bool] = mapped_column(Boolean, nullable=False)
    is_unique: Mapped[bool] = mapped_column(Boolean, nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False)
    validation_rules: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False)

    form_template: Mapped[FormTemplateModel] = relationship(back_populates="fields")
    options: Mapped[list["FormFieldOptionModel"]] = relationship(
        back_populates="form_field",
        cascade="all, delete-orphan",
        order_by="FormFieldOptionModel.sort_order",
    )


class FormFieldOptionModel(TimestampMixin, Base):
    __tablename__ = "form_field_options"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    form_field_id: Mapped[str] = mapped_column(
        ForeignKey("form_fields.id"), index=True, nullable=False
    )
    option_key: Mapped[str] = mapped_column(String(50), nullable=False)
    label: Mapped[str] = mapped_column(String(120), nullable=False)
    value: Mapped[str] = mapped_column(String(200), nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False)

    form_field: Mapped[FormFieldModel] = relationship(back_populates="options")
