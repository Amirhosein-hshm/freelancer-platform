from datetime import datetime

from pydantic import BaseModel

from app.domain.project.enums import ProjectStatus
from app.domain.review.enums import ReviewStatus


class ReviewResponse(BaseModel):
    review_id: str
    project_delivery_id: str
    project_id: str
    supervisor_user_id: str
    decision: ReviewStatus
    reject_reason: str | None
    notes: str | None
    reviewed_at: datetime | None


class ReviewDeliveryRequest(BaseModel):
    decision: ReviewStatus
    notes: str | None = None
    reject_reason: str | None = None


class ApproveDeliveryRequest(BaseModel):
    notes: str | None = None


class RejectDeliveryRequest(BaseModel):
    reason: str


class DeliveryReviewResponse(BaseModel):
    delivery_id: str
    project_id: str
    decision: ReviewStatus
    project_status: ProjectStatus
