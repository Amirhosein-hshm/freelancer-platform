from app.domain.shared.exceptions import (
    BusinessRuleViolationError,
    EntityNotFoundError,
    InvalidStateTransitionError,
)


class SupervisorReviewNotFoundError(EntityNotFoundError):
    """Raised when a SupervisorReview cannot be found for a delivery."""


class NotAssignedSupervisorError(BusinessRuleViolationError):
    """Raised when the actor is not the supervisor of the project's category."""


class DeliveryAlreadyReviewedError(InvalidStateTransitionError):
    """Raised when a delivery has already been reviewed by a supervisor."""
