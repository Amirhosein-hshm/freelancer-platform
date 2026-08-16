from app.domain.shared.exceptions import (
    BusinessRuleViolationError,
    EntityNotFoundError,
)


class FileAssetNotFoundError(EntityNotFoundError):
    pass


class InvalidFileContentError(BusinessRuleViolationError):
    pass
