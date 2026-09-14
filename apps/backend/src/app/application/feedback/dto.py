from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from app.domain.project.enums import ProjectStatus
from app.domain.review.enums import ReviewStatus
from app.domain.shared.types import EntityId


@dataclass(frozen=True)
class SubmitReviewCommand:
    actor_id: EntityId
    project_id: EntityId
    decision: ReviewStatus
    comment: str | None = None


@dataclass(frozen=True)
class SubmitReviewResult:
    review_id: EntityId
    project_id: EntityId
    decision: ReviewStatus
    project_status: ProjectStatus


@dataclass(frozen=True)
class SubmitRatingCommand:
    actor_id: EntityId
    project_id: EntityId
    score: int
    comment: str | None = None
    is_public: bool = False


@dataclass(frozen=True)
class SubmitRatingResult:
    rating_id: EntityId
    project_id: EntityId
    score: int


@dataclass(frozen=True)
class RatingResult:
    rating_id: EntityId
    customer_review_id: EntityId
    project_id: EntityId
    customer_user_id: EntityId
    freelancer_profile_id: EntityId
    score: int
    comment: str | None
    is_public: bool


@dataclass(frozen=True)
class GetFreelancerRatingsQuery:
    freelancer_profile_id: EntityId


@dataclass(frozen=True)
class GetFreelancerRatingsResult:
    ratings: list[RatingResult]
    average_score: Decimal | None


@dataclass(frozen=True)
class GetProjectRatingQuery:
    project_id: EntityId


@dataclass(frozen=True)
class GetProjectRatingResult:
    rating: RatingResult | None


@dataclass(frozen=True)
class CustomerReviewResult:
    review_id: EntityId
    project_id: EntityId
    project_delivery_id: EntityId
    customer_user_id: EntityId
    decision: ReviewStatus
    comment: str | None
    reviewed_at: datetime


@dataclass(frozen=True)
class GetCustomerReviewQuery:
    actor_id: EntityId
    review_id: EntityId


@dataclass(frozen=True)
class GetCustomerReviewResult:
    review: CustomerReviewResult


@dataclass(frozen=True)
class ListCustomerReviewsQuery:
    actor_id: EntityId
    project_id: EntityId


@dataclass(frozen=True)
class ListCustomerReviewsResult:
    project_id: EntityId
    reviews: list[CustomerReviewResult]


@dataclass(frozen=True)
class UpdateCustomerReviewCommand:
    actor_id: EntityId
    review_id: EntityId
    comment: str | None = None


@dataclass(frozen=True)
class UpdateCustomerReviewResult:
    review_id: EntityId


@dataclass(frozen=True)
class DeleteCustomerReviewCommand:
    actor_id: EntityId
    review_id: EntityId


@dataclass(frozen=True)
class DeleteCustomerReviewResult:
    review_id: EntityId


@dataclass(frozen=True)
class UpdateRatingCommand:
    actor_id: EntityId
    rating_id: EntityId
    score: int
    comment: str | None = None
    is_public: bool = False


@dataclass(frozen=True)
class UpdateRatingResult:
    rating_id: EntityId


@dataclass(frozen=True)
class DeleteRatingCommand:
    actor_id: EntityId
    rating_id: EntityId


@dataclass(frozen=True)
class DeleteRatingResult:
    rating_id: EntityId
