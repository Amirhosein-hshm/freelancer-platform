from app.domain.shared.exceptions import (
    BusinessRuleViolationError,
    EntityNotFoundError,
    InvalidStateTransitionError,
    UniqueConstraintViolationError,
)


class FormTemplateNotFoundError(EntityNotFoundError): ...


class FieldNotFoundError(EntityNotFoundError): ...


class DuplicateFieldKeyError(UniqueConstraintViolationError): ...


class DuplicateOptionKeyError(UniqueConstraintViolationError): ...


class FormTemplateAlreadyPublishedError(InvalidStateTransitionError): ...


class FormTemplateHasNoFieldsError(BusinessRuleViolationError): ...


class InvalidFieldOptionError(BusinessRuleViolationError): ...
