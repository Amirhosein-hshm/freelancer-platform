from app.domain.shared.exceptions import (
    BusinessRuleViolationError,
    EntityNotFoundError,
    UniqueConstraintViolationError,
)


class InvalidRatingScoreError(BusinessRuleViolationError):
    """Raised when a rating score is outside the valid 1..5 range."""


class RatingAlreadyExistsError(UniqueConstraintViolationError):
    """Raised when a project is rated more than once."""


class ProjectNotCompletedError(BusinessRuleViolationError):
    """Raised when an action requires the project to be completed."""


class CustomerReviewNotApprovedError(BusinessRuleViolationError):
    """Raised when rating requires an approved customer review."""


class CustomerReviewNotFoundError(EntityNotFoundError):
    """Raised when a customer review is not found."""


class RatingNotFoundError(EntityNotFoundError):
    """Raised when a rating is not found."""
