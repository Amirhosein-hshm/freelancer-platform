from app.domain.shared.exceptions import (
    BusinessRuleViolationError,
    UniqueConstraintViolationError,
)


class InvalidRatingScoreError(BusinessRuleViolationError):
    """Raised when a rating score is outside the valid 1..5 range."""


class RatingAlreadyExistsError(UniqueConstraintViolationError):
    """Raised when a project is rated more than once."""


class ProjectNotCompletedError(BusinessRuleViolationError):
    """Raised when an action requires the project to be completed."""
