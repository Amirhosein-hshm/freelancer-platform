```md
# TESTING.md — Testing Strategy (pytest)

## 1. General Principles

- Tests are written only for `domain` and `application` (Phase One); no real DB/Network
  is required.
- Tools: `pytest` (latest stable version), `pytest-cov` for coverage, `pytest-mock` if
  needed (prefer manual Fake instead of Mock for Repositories — more readable and less fragile).
- The test folder structure exactly mirrors `src/app`:
```

tests/
├── conftest.py
├── domain/
│ ├── iam/test_user.py
│ ├── iam/test_refresh_token.py
│ ├── freelancer/test_freelancer_profile.py
│ ├── project/test_project.py
│ ├── project/test_project_application.py
│ ├── project/test_project_delivery.py
│ ├── project/test_revision_policy.py
│ ├── ticketing/test_ticket.py
│ └── ...
└── application/
├── iam/test_register_user.py
├── iam/test_login_user.py
├── project/test_create_project.py
├── project/test_apply_for_project.py
├── project/test_accept_freelancer.py
├── project/test_request_revision.py
├── review/test_approve_delivery.py
├── feedback/test_submit_rating.py
└── ...

````

## 2. Entity Tests (Domain)

Goal: Every Entity method that changes state or checks a rule must have at least one happy-path
test and one test for every error path.

Test naming pattern: `test_<method>_<condition>_<expected_result>`

```python
# tests/domain/project/test_project.py
import pytest
from datetime import datetime, timezone
from app.domain.project.entities import Project
from app.domain.project.enums import ProjectStatus
from app.domain.project.exceptions import (
    ProjectAlreadyAssignedError,
    ProjectLockedError,
    InvalidProjectStatusTransitionError,
)

def make_project(**overrides) -> Project:
    defaults = dict(
        id="proj-1",
        status=ProjectStatus.COLLECTING_APPLICATIONS,
        selected_application_id=None,
        # ... other required fields with reasonable default values
    )
    defaults.update(overrides)
    return Project(**defaults)

class TestProjectAssignFreelancer:
    def test_assign_freelancer_from_collecting_applications_succeeds(self):
        project = make_project(status=ProjectStatus.COLLECTING_APPLICATIONS)
        now = datetime.now(timezone.utc)

        project.assign_freelancer("app-1", now)

        assert project.status == ProjectStatus.ASSIGNED
        assert project.selected_application_id == "app-1"

    def test_assign_freelancer_when_already_assigned_raises(self):
        project = make_project(
            status=ProjectStatus.COLLECTING_APPLICATIONS,
            selected_application_id="app-existing",
        )

        with pytest.raises(ProjectAlreadyAssignedError):
            project.assign_freelancer("app-2", datetime.now(timezone.utc))

    def test_assign_freelancer_when_project_completed_raises_locked(self):
        project = make_project(status=ProjectStatus.COMPLETED)

        with pytest.raises(ProjectLockedError):
            project.assign_freelancer("app-2", datetime.now(timezone.utc))

    def test_assign_freelancer_from_wrong_status_raises_transition_error(self):
        project = make_project(status=ProjectStatus.DRAFT)

        with pytest.raises(InvalidProjectStatusTransitionError):
            project.assign_freelancer("app-2", datetime.now(timezone.utc))
````

Key points:

- Use `Factory function`/`builder` (`make_project`) so each test only overrides related
  fields and remains readable.
- For Value Objects (`Email`, `Budget`, ...), separate validation tests:
  `test_email_with_invalid_format_raises_error`.
- For complete Enum/State Machine, a parametrized test for "all invalid transitions"
  is useful:

```python
@pytest.mark.parametrize("invalid_status", [
    ProjectStatus.DRAFT, ProjectStatus.ASSIGNED, ProjectStatus.COMPLETED,
])
def test_publish_from_invalid_status_raises(invalid_status):
    project = make_project(status=invalid_status)
    with pytest.raises(InvalidProjectStatusTransitionError):
        project.publish(datetime.now(timezone.utc))
```

## 3. Domain Services Tests

```python
# tests/domain/project/test_revision_policy.py
class TestRevisionPolicy:
    def test_can_request_when_under_limit_returns_true(self):
        assert RevisionPolicy.can_request_new_revision([r1, r2]) is True

    def test_can_request_when_at_limit_returns_false(self):
        assert RevisionPolicy.can_request_new_revision([r1, r2, r3]) is False
```

## 4. Use Case Tests (Application) — Fake Repositories

For each Repository Interface, we create an in-memory Fake in `tests/fakes/` that simulates
real behavior (`raise NotFoundError`, unique constraint, ...) — not just meaningless
Mock:

```python
# tests/fakes/fake_project_repository.py
class FakeProjectRepository(IProjectRepository):
    def __init__(self) -> None:
        self._store: dict[str, Project] = {}

    def add(self, project: Project) -> None:
        self._store[project.id] = project

    def get_by_id(self, project_id: str) -> Project:
        try:
            return self._store[project_id]
        except KeyError:
            raise ProjectNotFoundError(f"Project {project_id} not found.") from None

    def update(self, project: Project) -> None:
        self._store[project.id] = project

    # ... remaining Interface methods
```

Similar ones for `FakeUserRepository`, `FakeProjectApplicationRepository`,
`FakeUnitOfWork` (which only records commit/rollback as no-op or with a flag),
`FakeClock` (configurable fixed time), `FakeIdGenerator` (predictable sequential counter),
`FakePasswordHasher` (fake reversible hash for testing, **never use real hashing**),
`FakeTokenService`, `FakeAuthorizationService` (with a simple dictionary user_id -> permissions).

Example shared fixture file:

```python
# tests/conftest.py
import pytest

@pytest.fixture
def clock():
    return FakeClock(fixed_now=datetime(2026, 8, 2, tzinfo=timezone.utc))

@pytest.fixture
def id_generator():
    return FakeIdGenerator(prefix="test")

@pytest.fixture
def uow():
    return FakeUnitOfWork()
```

Complete Use Case test example:

```python
# tests/application/project/test_accept_freelancer.py
class TestAcceptFreelancerUseCase:
    def test_accept_freelancer_assigns_project_and_rejects_others(
        self, project_repo, application_repo, clock, uow
    ):
        project = make_project(status=ProjectStatus.COLLECTING_APPLICATIONS)
        app1 = make_application(project_id=project.id, status="APPLIED")
        app2 = make_application(project_id=project.id, status="APPLIED")
        project_repo.add(project)
        application_repo.add(app1)
        application_repo.add(app2)

        use_case = AcceptFreelancerUseCase(project_repo, application_repo, clock, uow)
        command = AcceptFreelancerCommand(actor_id=project.customer_user_id, application_id=app1.id)

        result = use_case.execute(command)

        assert result.status == "ASSIGNED"
        assert application_repo.get_by_id(app1.id).status == "ACCEPTED"
        assert application_repo.get_by_id(app2.id).status == "REJECTED"

    def test_accept_freelancer_by_non_owner_raises_permission_denied(
        self, project_repo, application_repo, clock, uow
    ):
        project = make_project(customer_user_id="owner-1")
        app1 = make_application(project_id=project.id)
        project_repo.add(project)
        application_repo.add(app1)
        use_case = AcceptFreelancerUseCase(project_repo, application_repo, clock, uow)

        with pytest.raises(PermissionDeniedError):
            use_case.execute(AcceptFreelancerCommand(actor_id="someone-else", application_id=app1.id))
```

## 5. Coverage and Testing Boundaries

- Minimum coverage: 90% on `domain` and `application` (checked with
  `pytest --cov=app/domain --cov=app/application --cov-report=term-missing --cov-fail-under=90`).
- Every Domain Exception must be triggered in at least one test (complete list in `DOMAIN.md`).
- Every Use Case must have at least: one happy-path test, one test for each Exception that
  it directly raises or passes through from Domain, and one test for the authorization path
  (if use case checks permission).
- Application tests must not rely on overly complex Fakes that reimplement business
  logic themselves — Fake should only simulate in-memory persistence.

## 6. Markers and pytest Configuration

```toml
# pyproject.toml
[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-ra -q --strict-markers"
markers = [
    "unit: fast unit tests (default for all tests in this project)",
    "slow: tests that execute slower (should not exist in Phase 1)",
]

[tool.coverage.run]
branch = true
source = ["app/domain", "app/application"]
```

## 7. Checklist Before Merging Any New Use Case/Entity

- [ ] Happy-path test is written.
- [ ] Tests for all Exception paths are written (with exact exception class, not generic).
- [ ] Required Fake Repository (if missing) is added.
- [ ] `pytest -q` is green.
- [ ] `mypy app/domain app/application` passes without errors.
- [ ] Coverage has not decreased (`--cov-fail-under=90`).

```

```
