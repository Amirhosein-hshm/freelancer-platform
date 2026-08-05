from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.db.base import Base, TimestampMixin


class SupervisorReviewModel(TimestampMixin, Base):
    __tablename__ = "supervisor_reviews"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    project_delivery_id: Mapped[str] = mapped_column(
        ForeignKey("project_deliveries.id"), index=True, nullable=False
    )
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id"), index=True, nullable=False)
    supervisor_user_id: Mapped[str] = mapped_column(String(36), index=True, nullable=False)
    decision: Mapped[str] = mapped_column(String(20), nullable=False)
    reject_reason: Mapped[str | None] = mapped_column(String(500), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
