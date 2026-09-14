from app.domain.shared.exceptions import (
    BusinessRuleViolationError,
    EntityNotFoundError,
)


class TicketNotFoundError(EntityNotFoundError):
    """Raised when a ticket cannot be found."""


class TicketClosedError(BusinessRuleViolationError):
    """Raised when a closed/archived ticket should not accept new messages."""


class NotTicketPartyError(BusinessRuleViolationError):
    """Raised when a user who is not a party of a two-party ticket acts on it."""


class TicketRelationshipError(BusinessRuleViolationError):
    """Raised when two users have no eligible relationship to open a ticket."""


class TicketMessageNotFoundError(EntityNotFoundError):
    """Raised when a ticket message cannot be found."""