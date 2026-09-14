from app.domain.shared.exceptions import (
    BusinessRuleViolationError,
    EntityNotFoundError,
    InvalidStateTransitionError,
    UniqueConstraintViolationError,
)


class FreelancerProfileNotFoundError(EntityNotFoundError): ...


class ResumeNotFoundError(EntityNotFoundError): ...


class PortfolioItemNotFoundError(EntityNotFoundError): ...


class DuplicateFreelancerProfileError(UniqueConstraintViolationError): ...


class FreelancerAlreadyApprovedError(InvalidStateTransitionError): ...


class FreelancerNotApprovedError(BusinessRuleViolationError): ...


class InvalidRateRangeError(BusinessRuleViolationError): ...
