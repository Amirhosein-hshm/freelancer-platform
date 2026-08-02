```md id="n8v2pz"
# AGENTS.md — Coding Agent Guide (opencode)

This file is the source of truth for every agent/tool that works on this repository
(opencode, Claude Code, or any other LLM). Before writing any line of code, read this file
and the following files:

1. `ARCHITECTURE.md` — layers, dependency rules, folder structure
2. `DOMAIN.md` — Entities, Value Objects, Repository Interfaces separated by each bounded context
3. `APPLICATION.md` — Use Cases, DTOs, Service Interfaces (Ports)
4. `ERROR_HANDLING.md` — Exception hierarchy and error contracts in each layer
5. `TESTING.md` — Rules for writing tests with pytest
6. `TODO.md` — Phased implementation checklist

## 1. Project Context

This backend is a freelance/project platform with 9 main bounded contexts extracted from
previous business analysis:
```

1. IAM (Identity & Access Management) -> app/{domain,application}/iam
2. Freelancer Management -> app/{domain,application}/freelancer
3. Category Management -> app/{domain,application}/category
4. Dynamic Form Engine -> app/{domain,application}/form
5. Project Management (Core Domain) -> app/{domain,application}/project
6. Quality Assurance / Supervisor Review -> app/{domain,application}/review
7. Feedback & Rating -> app/{domain,application}/feedback
8. Communication / Ticketing -> app/{domain,application}/ticketing
9. Reporting & Analytics (Read-Only) -> app/{domain,application}/reporting

````

Analytical sources: `domain-model.md`, `dbml-schema.md`, `full-analysis.md` (the three files
where the initial analysis was performed) — these must be kept alongside the project; every
Entity/Use Case/Rule must be Traceable to them. If you see a contradiction between these
files and the code, these files have priority unless changed by the user.

## 2. Phase One Scope (Important — Explicit Restriction)

**In Phase One, only two layers are implemented: `domain` and `application`.**
The `infrastructure` and `presentation` layers must only be created as **folder + empty
`__init__.py` + a short `README.md`** that specifies what will be implemented there in the
future (based on the Interfaces defined in `domain` and `application`). No real implementation
(FastAPI route, SQLAlchemy model, JWT library call) should be written in Phase One.

Every Interface/Port defined in `domain` or `application` must be written in a way that
allows future implementation in `infrastructure` without changing `domain`/`application`
(Dependency Inversion Principle).

## 3. Strict Architectural Rules (Non-negotiable)

- **Dependency direction**: `presentation -> application -> domain` and `infrastructure -> domain`
  (infrastructure implements domain/application interfaces, not the reverse).
  `domain` has no imports from `application`, `infrastructure`, or `presentation`.
  `application` has no imports from `infrastructure` or `presentation` and only works with
  Interfaces defined in `domain`.
- **No frameworks in domain/application**: No `import fastapi`, `import sqlalchemy`,
  `import pydantic`, ... are allowed in these two layers (except `dataclasses`, `typing`,
  `abc`, `enum`, `datetime`, `uuid` which are standard Python). If complex Validation is
  required, it is written manually in Entity/Value Object.
- **Entities must not be Anemic**: Business Rules that only depend on the Entity's own
  state must be written inside the Entity itself (for example `Project.can_be_cancelled()`),
  not in Use Cases. The Use Case only performs orchestration.
- **Repository Interfaces are in domain, Implementations will be in infrastructure in the future.**
- **Use Cases have one input (Request/Command DTO) and one output (Response/Result DTO)**
  and every Use Case is a class with one public method `execute(...)` (Command pattern).
- **Immutability where meaningful**: Value Objects and DTOs use `frozen=True` dataclass.
- **No duplicated Business Logic**: Rules needed in multiple Use Cases
  (for example "maximum 3 Revisions", "only one selected Freelancer") must be written at the
  Entity level or in a Domain Service (in `domain/<context>/services.py`), not copied into
  multiple Use Cases.

## 4. Naming Conventions

- Files and packages: `snake_case`
- Classes: `PascalCase`
- Interfaces (Ports) with prefix `I`: `IUserRepository`, `ITokenService`
- Enums: `PascalCase` for class, `UPPER_SNAKE` or lower for values — according to the third
  documentation (Persian) aligned with DBML (`project_status`, `user_status`, ...)
- Exceptions with suffix `Error`: `ProjectNotFoundError`, `InvalidStateTransitionError`
- Use Cases with suffix `UseCase`: `CreateProjectUseCase`, `ApproveDeliveryUseCase`
- Command/Query DTOs: `CreateProjectCommand`, `GetProjectQuery`
- Result DTOs: `ProjectResult`, `ProjectApplicationResult`

## 5. How the Agent Works on This Project

1. Every time before adding a new Entity/UseCase, check `DOMAIN.md`/`APPLICATION.md` to see
   whether it has already been defined (to prevent duplication and inconsistency).
2. For every new Entity, immediately write its unit tests in the same PR/commit
   (according to `TESTING.md`).
3. For every new Use Case:
   - Check required Repository/Service Interfaces; if they do not exist, define them first
     in `domain`.
   - Define Command/Result DTOs in `application/<context>/dto.py`.
   - Define dedicated Exceptions in `application/<context>/exceptions.py` or `domain`
     (depending on error type according to `ERROR_HANDLING.md`).
   - Write unit tests with Fake/Mock Repositories.
4. After every change, update `TODO.md` (check the checkboxes).
5. Never write real `infrastructure`/`presentation` code unless the user explicitly starts
   Phase Two.
6. Running tests: `pytest -q` must pass without any external dependency (DB, network) —
   because infrastructure does not exist yet, everything must be tested with Fake/In-Memory
   Repositories.

## 6. Definition of Done for Phase One

- [ ] All 9 bounded contexts have folder structures in `domain` and `application`.
- [ ] All Entities and Value Objects listed in `DOMAIN.md` are implemented.
- [ ] All Repository Interfaces in `DOMAIN.md` are implemented (as ABC).
- [ ] All Service Interfaces (Ports) in `APPLICATION.md` are implemented.
- [ ] All Core Flow Use Cases (`APPLICATION.md` Phase 1 section) are implemented.
- [ ] Test coverage on `domain` and `application` is at least 90%.
- [ ] `mypy --strict` passes on `domain` and `application` without errors.
- [ ] No forbidden imports (frameworks) exist in `domain`/`application`.

## 7. Tools and Versions

- Python >= 3.12
- pytest (latest stable version), `pytest-cov`, `pytest-mock`
- `mypy` for type checking (strict mode on domain/application)
- `ruff` for lint/format
- Dependency management: `pyproject.toml` (PEP 621) — no additional framework in Phase One

## 8. Common Commands

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests with coverage
pytest --cov=app/domain --cov=app/application --cov-report=term-missing

# Type check
mypy app/domain app/application

# Lint
ruff check app
````

```

```
