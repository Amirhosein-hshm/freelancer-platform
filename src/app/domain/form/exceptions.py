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


class FormTemplateNotPublishedError(InvalidStateTransitionError):
    """A project was submitted against a DRAFT or ARCHIVED template.

    Only reachable now that clients supply ``form_template_id`` directly; the old
    ``get_published_for_category`` lookup could only ever return a PUBLISHED template.
    """
