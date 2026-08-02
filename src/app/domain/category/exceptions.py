from app.domain.shared.exceptions import (
    BusinessRuleViolationError,
    EntityNotFoundError,
    UniqueConstraintViolationError,
)


class CategoryNotFoundError(EntityNotFoundError): ...


class DuplicateCategorySlugError(UniqueConstraintViolationError): ...


class SupervisorAlreadyAssignedError(BusinessRuleViolationError): ...


class SupervisorAssignmentNotFoundError(EntityNotFoundError): ...
