from datetime import datetime
from decimal import Decimal

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.db.base import Base, TimestampMixin


class FreelancerProfileModel(TimestampMixin, Base):
    __tablename__ = "freelancer_profiles"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True, nullable=False)
    current_level: Mapped[str | None] = mapped_column(String(20), index=True, nullable=True)
    approval_status: Mapped[str] = mapped_column(String(20), nullable=False)
    approved_by_user_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    approval_note: Mapped[str | None] = mapped_column(String(500), nullable=True)
    display_name: Mapped[str] = mapped_column(String(120), nullable=False)
    headline: Mapped[str | None] = mapped_column(String(200), nullable=True)
    bio: Mapped[str | None] = mapped_column(Text, nullable=True)
    country_code: Mapped[str | None] = mapped_column(String(10), nullable=True)
    city: Mapped[str | None] = mapped_column(String(120), nullable=True)
    timezone: Mapped[str | None] = mapped_column(String(64), nullable=True)
    hourly_rate_min: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    hourly_rate_max: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    is_available: Mapped[bool] = mapped_column(Boolean, nullable=False)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_by_user_id: Mapped[str | None] = mapped_column(String(36), nullable=True)


class FreelancerLevelHistoryModel(TimestampMixin, Base):
    __tablename__ = "freelancer_level_history"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    freelancer_profile_id: Mapped[str] = mapped_column(ForeignKey("freelancer_profiles.id"), index=True, nullable=False)
    old_level: Mapped[str | None] = mapped_column(String(20), nullable=True)
    new_level: Mapped[str] = mapped_column(String(20), index=True, nullable=False)
    assigned_by_user_id: Mapped[str] = mapped_column(String(36), nullable=False)
    reason: Mapped[str | None] = mapped_column(String(500), nullable=True)
    assigned_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class ResumeModel(TimestampMixin, Base):
    __tablename__ = "resumes"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    freelancer_profile_id: Mapped[str] = mapped_column(ForeignKey("freelancer_profiles.id"), index=True, nullable=False)
    file_asset_id: Mapped[str] = mapped_column(String(36), nullable=False)
    version_no: Mapped[int] = mapped_column(Integer, nullable=False)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_current: Mapped[bool] = mapped_column(Boolean, nullable=False)


class PortfolioItemModel(TimestampMixin, Base):
    __tablename__ = "portfolio_items"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    freelancer_profile_id: Mapped[str] = mapped_column(ForeignKey("freelancer_profiles.id"), index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    external_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    file_asset_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    display_order: Mapped[int] = mapped_column(Integer, nullable=False)
    is_featured: Mapped[bool] = mapped_column(Boolean, nullable=False)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
