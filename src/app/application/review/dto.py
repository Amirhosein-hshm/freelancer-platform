from dataclasses import dataclass
from datetime import datetime

from app.application.project.dto import ProjectResult
from app.application.shared.pagination import DEFAULT_PAGE_SIZE
from app.domain.project.enums import ProjectStatus
from app.domain.review.enums import ReviewStatus
from app.domain.shared.types import EntityId


@dataclass(frozen=True)
class GetSupervisorProjectsQuery:
    actor_id: EntityId
    supervisor_user_id: EntityId
    page: int = 1
    page_size: int = DEFAULT_PAGE_SIZE


@dataclass(frozen=True)
class GetSupervisorProjectsResult:
    projects: list[ProjectResult]
    total_items: int
    page: int
    page_size: int


@dataclass(frozen=True)
class GetPendingReviewsQuery:
    actor_id: EntityId
    supervisor_user_id: EntityId
    page: int = 1
    page_size: int = DEFAULT_PAGE_SIZE


@dataclass(frozen=True)
class ReviewResult:
    review_id: EntityId
    project_delivery_id: EntityId
    project_id: EntityId
    supervisor_user_id: EntityId
    decision: ReviewStatus
    reject_reason: str | None
    notes: str | None
    reviewed_at: datetime | None


@dataclass(frozen=True)
class GetPendingReviewsResult:
    reviews: list[ReviewResult]
    total_items: int
    page: int
    page_size: int


@dataclass(frozen=True)
class ApproveDeliveryCommand:
    actor_id: EntityId
    project_delivery_id: EntityId
    notes: str | None = None


@dataclass(frozen=True)
class RejectDeliveryCommand:
    actor_id: EntityId
    project_delivery_id: EntityId
    reason: str


@dataclass(frozen=True)
class ReviewDeliveryCommand:
    actor_id: EntityId
    project_delivery_id: EntityId
    decision: ReviewStatus
    notes: str | None = None
    reject_reason: str | None = None


@dataclass(frozen=True)
class ReviewDeliveryResult:
    delivery_id: EntityId
    project_id: EntityId
    decision: ReviewStatus
    project_status: ProjectStatus


@dataclass(frozen=True)
class GetSupervisorReviewQuery:
    actor_id: EntityId
    project_delivery_id: EntityId


@dataclass(frozen=True)
class GetSupervisorReviewResult:
    review: ReviewResult
