# TESTING.md — Testing Strategy (pytest)

## 1. General Principles

- `domain` and `application` tests require no real DB/Network — everything is tested with
  Fake/in-memory Repositories.
- As of Phase 2, `application` is async: every test that exercises a Use Case is an
  `async def test_...` and every Fake method is `async def`.
- Tools: `pytest` (latest stable), `pytest-cov` for coverage, `pytest-asyncio` for async
  tests, `pytest-mock` if needed (prefer manual Fakes over Mocks for Repositories — more
  readable and less fragile).
- The test folder structure mirrors `src/app`:

```
tests/
├── conftest.py
├── domain/
│   ├── iam/, freelancer/, category/, form/, project/, review/, feedback/, ticketing/
├── application/
│   ├── iam/, freelancer/, category/, form/, project/, review/, feedback/, ticketing/
├── infrastructure/          # Phase 2 — against a real Postgres, see §8
└── presentation/            # Phase 2 — httpx/TestClient + dependency_overrides, see §9
```

## 2. Entity Tests (Domain, sync)

Entities and their methods remain synchronous (no I/O), so their tests remain plain
`def test_...` (no `pytest-asyncio` needed here). Goal: every Entity method that changes
state or checks a rule must have at least one happy-path test and one test for every error
path.

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
```

For complete Enum/State Machine coverage, a parametrized test for "all invalid transitions"
is useful (see the previous revision of this document for the full example).

## 3. Domain Services Tests (sync)

```python
# tests/domain/project/test_revision_policy.py
class TestRevisionPolicy:
    def test_can_request_when_under_limit_returns_true(self):
        assert RevisionPolicy.can_request_new_revision([r1, r2]) is True

    def test_can_request_when_at_limit_returns_false(self):
        assert RevisionPolicy.can_request_new_revision([r1, r2, r3]) is False
```

## 4. Use Case Tests (Application, async) — Fake Repositories

For each Repository Interface, an async in-memory Fake lives in `tests/fakes/`, simulating
real behavior (`raise NotFoundError`, unique constraint, ...) — not a meaningless Mock:

```python
# tests/fakes/fake_project_repository.py
class FakeProjectRepository(IProjectRepository):
    def __init__(self) -> None:
        self._store: dict[str, Project] = {}

    async def add(self, project: Project) -> None:
        self._store[project.id] = project

    async def get_by_id(self, project_id: str) -> Project:
        try:
            return self._store[project_id]
        except KeyError:
            raise ProjectNotFoundError(f"Project {project_id} not found.") from None

    async def update(self, project: Project) -> None:
        self._store[project.id] = project

    # ... remaining Interface methods, all async def
```

Similarly for `FakeUserRepository`, `FakeProjectApplicationRepository`,
`FakeUnitOfWork` (async context manager, records commit/rollback as no-op or with a flag),
`FakeClock` (configurable fixed time, sync — no I/O), `FakeIdGenerator` (predictable
sequential counter, sync), `FakePasswordHasher` (fake reversible hash for testing, **never
use real hashing**), `FakeTokenService`, `FakeAuthorizationService` (a simple dictionary
`user_id -> set[permission_key]`, configurable per test so `authorize_owned_action` tests
can grant exactly the `_own`/`_any`/`_on_behalf` permission under test).

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

Complete async Use Case test example:

```python
# tests/application/project/test_accept_freelancer.py
class TestAcceptFreelancerUseCase:
    async def test_accept_freelancer_assigns_project_and_rejects_others(
        self, project_repo, application_repo, authz, clock, uow
    ):
        project = make_project(status=ProjectStatus.COLLECTING_APPLICATIONS)
        app1 = make_application(project_id=project.id, status="APPLIED")
        app2 = make_application(project_id=project.id, status="APPLIED")
        await project_repo.add(project)
        await application_repo.add(app1)
        await application_repo.add(app2)
        authz.grant(project.customer_user_id, "project.manage_own")

        use_case = AcceptFreelancerUseCase(authz, project_repo, application_repo, clock, uow)
        command = AcceptFreelancerCommand(actor_id=project.customer_user_id, application_id=app1.id)

        result = await use_case.execute(command)

        assert result.status == "ASSIGNED"
        assert (await application_repo.get_by_id(app1.id)).status == "ACCEPTED"
        assert (await application_repo.get_by_id(app2.id)).status == "REJECTED"

    async def test_accept_freelancer_by_non_owner_without_manage_any_raises_permission_denied(
        self, project_repo, application_repo, authz, clock, uow
    ):
        project = make_project(customer_user_id="owner-1")
        app1 = make_application(project_id=project.id)
        await project_repo.add(project)
        await application_repo.add(app1)
        use_case = AcceptFreelancerUseCase(authz, project_repo, application_repo, clock, uow)

        with pytest.raises(PermissionDeniedError):
            await use_case.execute(AcceptFreelancerCommand(actor_id="someone-else", application_id=app1.id))
```

## 5. Coverage and Testing Boundaries

- Minimum coverage: 90% on `domain` and `application` (checked with
  `pytest --cov=app/domain --cov=app/application --cov-report=term-missing --cov-fail-under=90`).
- Every Domain Exception must be triggered in at least one test (complete list in `DOMAIN.md`).
- Every Use Case must have at least: one happy-path test, one test for each Exception it
  directly raises or passes through from Domain, and one test for each authorization tier it
  checks (`_own`, `_any`, `_on_behalf` where applicable).
- Application tests must not rely on overly complex Fakes that reimplement business
  logic themselves — Fakes only simulate in-memory persistence.

## 6. Markers and pytest Configuration

```toml
# pyproject.toml
[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-ra -q --strict-markers"
asyncio_mode = "auto"   # so async def test_... doesn't need @pytest.mark.asyncio everywhere
markers = [
    "unit: fast unit tests (default for domain/application)",
    "integration: tests requiring a real Postgres (infrastructure)",
    "slow: tests that execute slower",
]

[tool.coverage.run]
branch = true
source = ["app/domain", "app/application"]
```

## 7. Checklist Before Merging Any New Use Case/Entity

- [ ] Happy-path test is written.
- [ ] Tests for all Exception paths are written (with exact exception class, not generic).
- [ ] Required async Fake Repository (if missing) is added.
- [ ] Authorization tests cover every permission tier the use case checks.
- [ ] `pytest -q` is green.
- [ ] `mypy app/domain app/application` passes without errors.
- [ ] Coverage has not decreased (`--cov-fail-under=90`).

## 8. Infrastructure Tests (Phase 2, real Postgres)

- Run against a real Postgres — via the docker-compose `db` service pointed at a separate
  test database/schema — not a different DB engine (e.g. SQLite), which could hide
  dialect-specific bugs.
- At minimum cover: one repository's `add`+`get_by_id` round trip per bounded context; the
  `SqlAlchemyAuthorizationService` returning correct results for a seeded role/permission
  pair, **and** a test that revokes a permission from a role in the seeded test DB and
  asserts the authorization outcome changes accordingly (proving `AUTHORIZATION.md` §6's
  data-source contract — no hardcoded shortcut); the atomic project/ticket code generator
  producing sequential, non-colliding codes under concurrent calls (e.g. `asyncio.gather` of
  several `next_code()` calls).
- Mark these with `@pytest.mark.integration` so they can be excluded from the fast
  domain/application test run (`pytest -m "not integration"`).

## 9. Presentation Tests (Phase 2, no real DB)

- Use FastAPI's `TestClient`/`httpx.AsyncClient` with `app.dependency_overrides` pointed at
  the same async Fakes used in `tests/application/fakes` — do not spin up a real database
  for these tests.
- Cover: the envelope shape of one success and one error response per HTTP status code in
  the `ERROR_HANDLING.md` mapping table (404/409/422/403/400); that `GET /api/v1/auth/me`
  returns the `roles`/`permissions` shape and no other endpoint does (`API_DESIGN.md` §6);
  pagination meta shape on at least one list endpoint.
