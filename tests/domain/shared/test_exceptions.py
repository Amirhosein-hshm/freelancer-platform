from app.domain.shared.exceptions import (
    BusinessRuleViolationError,
    DomainError,
    EntityNotFoundError,
    InvalidStateTransitionError,
    UniqueConstraintViolationError,
)


class TestDomainExceptionHierarchy:
    def test_all_base_errors_inherit_domain_error(self):
        for error_cls in (
            EntityNotFoundError,
            InvalidStateTransitionError,
            BusinessRuleViolationError,
            UniqueConstraintViolationError,
        ):
            assert issubclass(error_cls, DomainError)

    def test_all_base_errors_inherit_exception(self):
        assert issubclass(DomainError, Exception)

    def test_error_carries_message(self):
        error = EntityNotFoundError("Project p-1 not found.")
        assert str(error) == "Project p-1 not found."
