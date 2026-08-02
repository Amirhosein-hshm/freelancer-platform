from app.domain.shared.exceptions import (
    BusinessRuleViolationError,
    EntityNotFoundError,
    InvalidStateTransitionError,
    UniqueConstraintViolationError,
)


class UserNotFoundError(EntityNotFoundError): ...


class DuplicateEmailError(UniqueConstraintViolationError): ...


class InvalidCredentialsError(BusinessRuleViolationError): ...


class UserAlreadyBlockedError(InvalidStateTransitionError): ...


class UserNotActiveError(BusinessRuleViolationError): ...


class InvalidRefreshTokenError(BusinessRuleViolationError): ...


class RefreshTokenNotFoundError(EntityNotFoundError): ...


class RoleNotFoundError(EntityNotFoundError): ...


class PermissionNotFoundError(EntityNotFoundError): ...


class UserRoleNotFoundError(EntityNotFoundError): ...


class RoleAlreadyAssignedError(BusinessRuleViolationError): ...


class SystemRoleImmutableError(BusinessRuleViolationError): ...


class InvalidEmailError(BusinessRuleViolationError): ...


class InvalidPhoneNumberError(BusinessRuleViolationError): ...
