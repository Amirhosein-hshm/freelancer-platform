from dataclasses import dataclass
from datetime import datetime

from app.domain.feedback.exceptions import InvalidRatingScoreError
from app.domain.review.enums import ReviewStatus
from app.domain.shared.entity import Entity
from app.domain.shared.types import EntityId


@dataclass(eq=False)
class CustomerReview(Entity):
    """Final customer verdict on a delivered project."""

    project_id: EntityId
    project_delivery_id: EntityId
    customer_user_id: EntityId
    decision: ReviewStatus
    comment: str | None
    reviewed_at: datetime


@dataclass(eq=False)
class Rating(Entity):
    """1..5 score given by the customer after the project is completed."""

    customer_review_id: EntityId
    project_id: EntityId
    customer_user_id: EntityId
    freelancer_profile_id: EntityId
    score: int
    comment: str | None
    is_public: bool

    def __post_init__(self) -> None:
        if not 1 <= self.score <= 5:
            raise InvalidRatingScoreError(
                f"Rating score must be between 1 and 5, got {self.score}."
            )
