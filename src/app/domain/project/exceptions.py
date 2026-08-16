from app.domain.shared.exceptions import (
    BusinessRuleViolationError,
    EntityNotFoundError,
    InvalidStateTransitionError,
    UniqueConstraintViolationError,
)


class ProjectNotFoundError(EntityNotFoundError): ...


class ApplicationNotFoundError(EntityNotFoundError): ...


class DeliveryNotFoundError(EntityNotFoundError): ...


class RevisionRequestNotFoundError(EntityNotFoundError): ...


class ProjectLockedError(BusinessRuleViolationError): ...


class ProjectAlreadyAssignedError(BusinessRuleViolationError): ...


class InvalidProjectStatusTransitionError(InvalidStateTransitionError): ...


class ApplicationAlreadyDecidedError(InvalidStateTransitionError): ...


class DuplicateApplicationError(UniqueConstraintViolationError): ...


class MaxRevisionsExceededError(BusinessRuleViolationError): ...


class ApplicationDeadlineExpiredError(BusinessRuleViolationError): ...


class FreelancerNotEligibleError(BusinessRuleViolationError): ...


class InvalidBudgetError(BusinessRuleViolationError): ...


class InvalidProjectCodeError(BusinessRuleViolationError): ...
