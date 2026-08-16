from app.domain.shared.exceptions import (
    BusinessRuleViolationError,
    EntityNotFoundError,
    InvalidStateTransitionError,
    ReferencedEntityConflictError,
    UniqueConstraintViolationError,
)


class FormTemplateNotFoundError(EntityNotFoundError): ...


class FieldNotFoundError(EntityNotFoundError): ...


class DuplicateFieldKeyError(UniqueConstraintViolationError): ...


class DuplicateOptionKeyError(UniqueConstraintViolationError): ...


class FormTemplateAlreadyPublishedError(InvalidStateTransitionError): ...


class FormTemplateHasNoFieldsError(BusinessRuleViolationError): ...


class InvalidFieldOptionError(BusinessRuleViolationError): ...


class OptionNotFoundError(EntityNotFoundError): ...


class FormTemplateHasActiveReferencesError(ReferencedEntityConflictError):
    """Raised when deleting a form template that is published or referenced by active projects."""
