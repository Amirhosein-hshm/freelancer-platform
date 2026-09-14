from dataclasses import dataclass
from datetime import datetime

from app.domain.review.enums import ReviewStatus
from app.domain.shared.entity import Entity
from app.domain.shared.exceptions import InvalidStateTransitionError
from app.domain.shared.types import EntityId


@dataclass(eq=False)
class SupervisorReview(Entity):
    """QA review of a single project delivery by its assigned category supervisor.

    A review is created (PENDING) when a delivery is routed to supervisor review and is
    then decided through ``approve``/``reject``. ``reviewed_at`` records when the
    decision was made.
    """

    project_delivery_id: EntityId
    project_id: EntityId
    supervisor_user_id: EntityId
    decision: ReviewStatus = ReviewStatus.PENDING
    reject_reason: str | None = None
    notes: str | None = None
    reviewed_at: datetime | None = None

    def approve(self, notes: str | None, at: datetime) -> None:
        self._ensure_pending()
        self.decision = ReviewStatus.APPROVED
        self.notes = notes
        self.reviewed_at = at

    def reject(self, reason: str, at: datetime) -> None:
        self._ensure_pending()
        self.decision = ReviewStatus.REJECTED
        self.reject_reason = reason
        self.reviewed_at = at

    def _ensure_pending(self) -> None:
        if self.decision != ReviewStatus.PENDING:
            raise InvalidStateTransitionError(
                f"Review {self.id} is already '{self.decision.value}' and cannot be re-decided."
            )
