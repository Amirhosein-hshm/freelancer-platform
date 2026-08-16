from app.domain.shared.exceptions import (
    BusinessRuleViolationError,
    EntityNotFoundError,
    ReferencedEntityConflictError,
    UniqueConstraintViolationError,
)


class CategoryNotFoundError(EntityNotFoundError): ...


class DuplicateCategorySlugError(UniqueConstraintViolationError): ...


class SupervisorAlreadyAssignedError(BusinessRuleViolationError): ...


class SupervisorAssignmentNotFoundError(EntityNotFoundError): ...


class CategoryHasActiveReferencesError(ReferencedEntityConflictError):
    """Raised when deleting a category that still has child categories or active projects."""

    def __init__(self, message: str, children_count: int = 0, active_projects_count: int = 0) -> None:
        super().__init__(message)
        self.children_count = children_count
        self.active_projects_count = active_projects_count
