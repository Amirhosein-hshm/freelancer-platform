class ApplicationError(Exception):
    """Base class for every application-level error (orchestration/authorization)."""


class InvalidTokenError(ApplicationError):
    """Raised when an access token is malformed/invalid (maps to HTTP 401)."""


class ExpiredTokenError(ApplicationError):
    """Raised when an access token is valid but expired (maps to HTTP 401)."""


class PermissionDeniedError(ApplicationError):
    """Raised when the actor is not allowed to perform the operation (maps to HTTP 403)."""


class ValidationError(ApplicationError):
    """Raised when command/input validation fails (maps to HTTP 400)."""


class FormValidationError(ValidationError):
    """Raised when dynamic form values fail validation against the form template."""


class ExternalServiceError(ApplicationError):
    """Raised when an external port (token, storage, notification, ...) fails."""
