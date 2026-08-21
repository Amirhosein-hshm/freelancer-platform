from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.db.base import Base, TimestampMixin


class ProjectModel(TimestampMixin, Base):
    __tablename__ = "projects"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    project_code: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    customer_user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)
    category_id: Mapped[str] = mapped_column(ForeignKey("categories.id"), index=True, nullable=False)
    form_template_id: Mapped[str] = mapped_column(String(36), nullable=False)
    required_level: Mapped[str | None] = mapped_column(String(20), nullable=True)
    assigned_supervisor_user_id: Mapped[str | None] = mapped_column(ForeignKey("users.id"), index=True, nullable=True)
    selected_application_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    visibility: Mapped[str] = mapped_column(String(20), nullable=False)
    priority: Mapped[str] = mapped_column(String(20), nullable=False)
    budget_type: Mapped[str] = mapped_column(String(20), nullable=False)
    fixed_amount: Mapped[Decimal | None] = mapped_column(Numeric(14, 2), nullable=True)
    min_amount: Mapped[Decimal | None] = mapped_column(Numeric(14, 2), nullable=True)
    max_amount: Mapped[Decimal | None] = mapped_column(Numeric(14, 2), nullable=True)
    currency_code: Mapped[str] = mapped_column(String(10), nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False)
    application_deadline: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    start_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    due_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    cancelled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    locked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_by_user_id: Mapped[str | None] = mapped_column(String(36), nullable=True)


class ProjectApplicationModel(TimestampMixin, Base):
    __tablename__ = "project_applications"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id"), index=True, nullable=False)
    freelancer_profile_id: Mapped[str] = mapped_column(ForeignKey("freelancer_profiles.id"), index=True, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    cover_letter: Mapped[str | None] = mapped_column(Text, nullable=True)
    proposed_amount: Mapped[Decimal | None] = mapped_column(Numeric(14, 2), nullable=True)
    proposed_days: Mapped[int | None] = mapped_column(Integer, nullable=True)
    applied_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    decided_by_user_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    decided_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    decision_note: Mapped[str | None] = mapped_column(String(500), nullable=True)
    withdrawn_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    submitted_by_user_id: Mapped[str | None] = mapped_column(String(36), nullable=True)


class ProjectDeliveryModel(TimestampMixin, Base):
    __tablename__ = "project_deliveries"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id"), index=True, nullable=False)
    version_no: Mapped[int] = mapped_column(Integer, nullable=False)
    submitted_by_user_id: Mapped[str] = mapped_column(String(36), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    delivery_note: Mapped[str | None] = mapped_column(Text, nullable=True)
    submitted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    reviewer_user_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    superseded_by_delivery_id: Mapped[str | None] = mapped_column(ForeignKey("project_deliveries.id"), nullable=True)
    # JSONB (not JSON): list_by_file_asset_id relies on the containment operator, which
    # plain JSON does not support (it degrades to a LIKE that Postgres rejects).
    file_asset_ids: Mapped[list[str]] = mapped_column(JSONB, nullable=False)


class ProjectRevisionRequestModel(TimestampMixin, Base):
    __tablename__ = "project_revision_requests"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id"), index=True, nullable=False)
    project_delivery_id: Mapped[str | None] = mapped_column(
        ForeignKey("project_deliveries.id"), index=True, nullable=True
    )
    requested_by_user_id: Mapped[str] = mapped_column(String(36), nullable=False)
    requested_to_user_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    round_no: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    resolved_by_user_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    requested_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)


class ProjectStatusHistoryModel(TimestampMixin, Base):
    __tablename__ = "project_status_history"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id"), index=True, nullable=False)
    from_status: Mapped[str | None] = mapped_column(String(30), nullable=True)
    to_status: Mapped[str] = mapped_column(String(30), nullable=False)
    changed_by_user_id: Mapped[str] = mapped_column(String(36), nullable=False)
    reason: Mapped[str | None] = mapped_column(String(500), nullable=True)
    changed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
