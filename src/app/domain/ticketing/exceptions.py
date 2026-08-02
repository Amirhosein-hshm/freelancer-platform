from app.domain.shared.exceptions import (
    BusinessRuleViolationError,
    EntityNotFoundError,
)


class TicketNotFoundError(EntityNotFoundError):
    """Raised when a ticket cannot be found."""


class TicketClosedError(BusinessRuleViolationError):
    """Raised when a closed/archived ticket should not accept new messages."""


class NotTicketParticipantError(BusinessRuleViolationError):
    """Raised when a user who is not a ticket participant performs an action."""
