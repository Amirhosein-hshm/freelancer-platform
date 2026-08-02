class ApplicationError(Exception):
    """Base class for every application-level error (orchestration/authorization)."""


class PermissionDeniedError(ApplicationError):
    """Raised when the actor is not allowed to perform the operation (maps to HTTP 403)."""


class ValidationError(ApplicationError):
    """Raised when command/input validation fails (maps to HTTP 400)."""


class FormValidationError(ValidationError):
    """Raised when dynamic form values fail validation against the form template."""


class ExternalServiceError(ApplicationError):
    """Raised when an external port (token, storage, notification, ...) fails."""
