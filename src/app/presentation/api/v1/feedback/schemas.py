from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field

from app.domain.project.enums import ProjectStatus
from app.domain.review.enums import ReviewStatus


class SubmitReviewRequest(BaseModel):
    project_id: str
    decision: ReviewStatus
    comment: str | None = None


class SubmitReviewResponse(BaseModel):
    review_id: str
    project_id: str
    decision: ReviewStatus
    project_status: ProjectStatus


class SubmitRatingRequest(BaseModel):
    project_id: str
    score: int = Field(..., ge=1, le=5)
    comment: str | None = None
    is_public: bool = False


class SubmitRatingResponse(BaseModel):
    rating_id: str
    project_id: str
    score: int


class RatingResponse(BaseModel):
    rating_id: str
    customer_review_id: str
    project_id: str
    customer_user_id: str
    freelancer_profile_id: str
    score: int
    comment: str | None
    is_public: bool


class UpdateRatingRequest(BaseModel):
    score: int = Field(..., ge=1, le=5)
    comment: str | None = None
    is_public: bool = False


class CustomerReviewResponse(BaseModel):
    review_id: str
    project_id: str
    project_delivery_id: str
    customer_user_id: str
    decision: ReviewStatus
    comment: str | None
    reviewed_at: datetime


class CustomerReviewsResponse(BaseModel):
    project_id: str
    reviews: list[CustomerReviewResponse]


class UpdateCustomerReviewRequest(BaseModel):
    comment: str | None = None


class ProjectRatingResponse(BaseModel):
    rating: RatingResponse | None


class FreelancerRatingsResponse(BaseModel):
    ratings: list[RatingResponse]
    average_score: Decimal | None
