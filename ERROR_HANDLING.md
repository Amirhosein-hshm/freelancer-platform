# ERROR_HANDLING.md — Error Handling Strategy

## 1. General Philosophy

- No layer should leak raw Python Exceptions (`ValueError`, `KeyError`, ...) directly
  to the outside; all meaningful Exceptions must inherit from the project's dedicated
  hierarchy.
- **Domain errors** = violation of a business rule or absence of an Entity; these are
  defined in `domain/*/exceptions.py` and are **independent of HTTP/Framework**.
- **Application errors** = errors related to orchestration, authorization, or input
  validation (not the Entity itself); these are defined in
  `application/*/exceptions.py` or `application/shared/exceptions.py`.
- **Infrastructure errors** = DB/Network/External API errors; these are translated
  (wrapped) inside `infrastructure` into one of the Domain/Application errors before
  reaching `application` — `application` never sees `SQLAlchemyError`,
  `asyncpg.PostgresError`, or `ConnectionError` directly.
- **Presentation** is the only place where Exceptions are mapped to HTTP status codes, via
  a global FastAPI Exception Handler (`presentation/core/error_handlers.py`) — see
  `API_DESIGN.md` for the exact envelope shape and `PRESENTATION.md` §6 for the
  implementation pattern (one handler per base class, automatic `code` derivation).

## 2. Base Hierarchy

```
Exception
└── DomainError (domain/shared/exceptions.py)
    ├── EntityNotFoundError                  -> HTTP 404
    ├── InvalidStateTransitionError          -> HTTP 409
    ├── BusinessRuleViolationError           -> HTTP 422
    └── UniqueConstraintViolationError       -> HTTP 409

Exception
└── ApplicationError (application/shared/exceptions.py)
    ├── PermissionDeniedError                -> HTTP 403
    ├── ValidationError                      -> HTTP 400
    │   └── FormValidationError
    └── ExternalServiceError                 -> HTTP 502/503
```

Each context is allowed to create dedicated subclasses from these bases (for example
`ProjectNotFoundError(EntityNotFoundError)`) but must never inherit directly from
`Exception`.

## 3. Entity-Level Contract (Domain)

- Entity methods that detect a rule violation must immediately raise a dedicated
  Exception, not use `assert` and not return `None`/`False` instead of an error
  (except query methods like `is_locked() -> bool` which intentionally return boolean).
  Entity methods remain synchronous (`def`, not `async def`) — they are pure in-memory
  state transitions with no I/O.
- Error messages must include enough identifier/context information for debugging but
  must not expose sensitive information (passwords, raw tokens).
- Example:

```python
def assign_freelancer(self, application_id: EntityId, at: datetime) -> None:
    if self.is_locked():
        raise ProjectLockedError(f"Project {self.id} is locked (status={self.status}).")
    if self.selected_application_id is not None:
        raise ProjectAlreadyAssignedError(
            f"Project {self.id} already has selected_application_id={self.selected_application_id}."
        )
    if self.status != ProjectStatus.COLLECTING_APPLICATIONS:
        raise InvalidProjectStatusTransitionError(
            f"Cannot assign freelancer from status={self.status}."
        )
    self.selected_application_id = application_id
    self.status = ProjectStatus.ASSIGNED
```

## 4. Use Case-Level Contract (Application, async)

The Use Case manages three categories of errors:

1. **Authorization** — before any write operation,
   `await authorization_service.require_permission(...)` or the
   `await authorize_owned_action(...)` two-tier helper (`AUTHORIZATION.md` §3.1).

2. **Input Validation** — before calling Repository/Entity, the format/completeness of
   Command DTO is checked (`ValidationError`/`FormValidationError`); this validation is
   "structural" (for example, all required form fields are filled), not deep business
   logic (which goes to Entity).

3. **Propagation** — Domain Exceptions (`EntityNotFoundError` and its subclasses) that
   come from Repository/Entity are **propagated unchanged**; the Use Case does not catch
   them unless it wants to create a higher-level error (for example, catching
   `EntityNotFoundError` in a specific scenario and converting it into a friendlier
   message — this must be case-specific and documented, not the default behavior).

Complete error handling Use Case example (async):

```python
class AcceptFreelancerUseCase(UseCase[AcceptFreelancerCommand, ProjectResult]):
    async def execute(self, request: AcceptFreelancerCommand) -> ProjectResult:
        application = await self._application_repo.get_by_id(request.application_id)  # ApplicationNotFoundError
        project = await self._project_repo.get_by_id(application.project_id)          # ProjectNotFoundError

        await authorize_owned_action(
            self._authz, request.actor_id, project.customer_user_id,
            "project.manage_own", "project.manage_any",
        )

        async with self._uow:
            application.accept(request.actor_id, self._clock.now())
            project.assign_freelancer(application.id, self._clock.now())
            for other in await self._application_repo.list_by_project(project.id):
                if other.id != application.id and other.status in (
                    ProjectApplicationStatus.APPLIED, ProjectApplicationStatus.SHORTLISTED
                ):
                    other.reject(request.actor_id, self._clock.now(), note="Another freelancer selected.")
                    await self._application_repo.update(other)
            await self._application_repo.update(application)
            await self._project_repo.update(project)
            await self._uow.commit()

        return ProjectResult.from_entity(project)
```

Note: If any Exception occurs inside the `async with self._uow:` block, `__aexit__` must
perform rollback (this contract must be documented in the `IUnitOfWork` Interface) — the
Use Case itself does not need explicit `try/except/rollback`.

## 5. Fail Fast in Use Case Input

Every Command DTO must be superficially validated at the beginning of `execute` (not in
the dataclass's own `__post_init__`, because the dataclass in application may need to be
created without validation — for example, in tests). Preference: a helper method
`validate()` on the DTO itself or a separate function
`validate_create_project_command(cmd)` that is called at the beginning of `execute`.

## 6. Logging

- `domain` never logs (completely pure/side-effect-free except for mutation of its own state).
- `application` can use an `ILogger` Port (optional, in `shared/ports.py`) to log
  `ExternalServiceError` and unexpected cases; logging must never replace raising an
  appropriate Exception.
- `infrastructure` should log the original raw exception (SQLAlchemy/network/etc.) before
  translating and re-raising it as a domain/application error, so the original stack trace
  is not lost for debugging even though it never reaches `application`.

## 7. HTTP Mapping — Now Implemented (see `API_DESIGN.md`, `PRESENTATION.md`)

| Base Exception                            | HTTP Status | Example                                                |
| ----------------------------------------- | ----------- | ------------------------------------------------------ |
| `EntityNotFoundError`                     | 404         | `ProjectNotFoundError`                                 |
| `InvalidStateTransitionError`             | 409         | `ProjectLockedError`, `FreelancerAlreadyApprovedError` |
| `BusinessRuleViolationError`              | 422         | `MaxRevisionsExceededError`, `InvalidRatingScoreError` |
| `UniqueConstraintViolationError`          | 409         | `DuplicateEmailError`, `DuplicateApplicationError`     |
| `PermissionDeniedError`                   | 403         | —                                                      |
| `ValidationError` / `FormValidationError` | 400         | —                                                      |
| `ExternalServiceError`                    | 502         | —                                                      |
| Any other unknown Exception               | 500         | logged with severity=error, generic message returned   |

This mapping is implemented in a global FastAPI Exception Handler
(`presentation/core/error_handlers.py`), with the error `code` field derived automatically
from the exception class name (strip the `Error` suffix, convert to `UPPER_SNAKE_CASE`) —
see `API_DESIGN.md` §3–4 for the exact response envelope shape and `PRESENTATION.md` §6 for
the handler registration pattern (one handler per base class, not per subclass).

## 8. Error Testing Requirements (Reference to `TESTING.md`)

Every business rule that raises an Exception must have at least one separate test that:

1. Creates the conditions for violating the rule,
2. Verifies using `pytest.raises(SpecificExceptionClass)` (not generic `Exception`),
3. If necessary, also checks the error message or additional exception attributes.

For `presentation`, add a corresponding test asserting the HTTP status and the
`ErrorEnvelope` shape (`code`, `message`) for at least one exception per base class in the
table above (see `TESTING.md` §8).
