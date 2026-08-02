from dataclasses import dataclass
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
