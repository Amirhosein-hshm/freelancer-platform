class DomainError(Exception):
    """Base class for every domain-level error in the project."""


class EntityNotFoundError(DomainError):
    """Raised when an entity cannot be found (maps to HTTP 404 in Phase 2)."""


class InvalidStateTransitionError(DomainError):
    """Raised when a state transition is not allowed (maps to HTTP 409)."""


class BusinessRuleViolationError(DomainError):
    """Raised when a business rule is violated (maps to HTTP 422)."""


class UniqueConstraintViolationError(DomainError):
    """Raised when a unique constraint is violated (maps to HTTP 409)."""
