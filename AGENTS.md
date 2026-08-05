# AGENTS.md — Coding Agent Guide (opencode)

This file is the source of truth for every agent/tool that works on this repository
(opencode, Claude Code, or any other LLM). Before writing any line of code, read this file
and the following files:

1. `ARCHITECTURE.md` — layers, dependency rules, folder structure (5 packages:
   `domain`, `application`, `infrastructure`, `presentation`, `bootstrap`)
2. `DOMAIN.md` — Entities, Value Objects, Repository Interfaces per bounded context
3. `APPLICATION.md` — Use Cases, DTOs, Service Interfaces (Ports)
4. `AUTHORIZATION.md` — RBAC model, permission-key conventions, the Self vs. On-Behalf
   pattern rule, and the RBAC data-source contract
5. `ERROR_HANDLING.md` — Exception hierarchy and error contracts in each layer
6. `API_DESIGN.md` — response envelope, pagination, error shape, route/OpenAPI conventions
7. `PRESENTATION.md` — FastAPI structure, composition-root wiring, auth, WebSocket
8. `INFRASTRUCTURE.md` — SQLAlchemy/Postgres, JWT, password hashing, seed strategy
9. `DOCKER.md` — Dockerfile, docker-compose, seeding-on-startup pattern
10. `TESTING.md` — Rules for writing tests with pytest (unit + infra + presentation)
11. `TODO.md` — Phased implementation checklist

## 1. Project Context

This backend is a freelance/project platform with 9 bounded contexts:

```
1. IAM (Identity & Access Management)     -> app/{domain,application}/iam
2. Freelancer Management                  -> app/{domain,application}/freelancer
3. Category Management                    -> app/{domain,application}/category
4. Dynamic Form Engine                    -> app/{domain,application}/form
5. Project Management (Core Domain)       -> app/{domain,application}/project
6. Quality Assurance / Supervisor Review  -> app/{domain,application}/review
7. Feedback & Rating                      -> app/{domain,application}/feedback
8. Communication / Ticketing              -> app/{domain,application}/ticketing
9. Reporting & Analytics (Read-Only)      -> app/{domain,application}/reporting
```

Roles are fixed and closed: `admin`, `customer`, `freelancer`, `supervisor`. Never add a new
role or a per-resource role/permission table (e.g. no `project_supervisor_role`) — see
`AUTHORIZATION.md` for why flat RBAC + ownership checks is sufficient here.

## 2. Project Phases (current status)

- **Phase 1 — `domain` + `application`: functionally complete, actively hardened.** All 9
  contexts have Entities, Repository Interfaces, and Use Cases, including owned-resource
  authorization (`_own`/`_any` via `authorize_owned_action`) and the Self vs. On-Behalf
  pattern (`AUTHORIZATION.md`). Treat this layer as stable: new changes here should be
  surgical fixes or additions that follow existing conventions, not architectural rewrites.
  Before starting Phase 2 work, verify with the person whether any previously agreed
  authorization fixes (e.g. the `CreateProject` self/on-behalf split) are fully applied in
  code — do not assume the spec files are 100% in sync with the implementation; if you find
  a mismatch, flag it rather than silently "fixing" the docs to match unverified code.
- **Phase 2 — `infrastructure` + `presentation` + `bootstrap`: STARTING NOW.** Real
  implementations belong here: FastAPI routers, SQLAlchemy repositories, JWT/Argon2, Alembic
  migrations, Docker. Follow `PRESENTATION.md`, `INFRASTRUCTURE.md`, `DOCKER.md` exactly for
  folder layout and conventions — do not invent a different envelope, DI approach, or folder
  structure.
- **Mandatory first step of Phase 2:** convert the `application` layer to async
  (`UseCase.execute` and every port/repository method become `async def`, `await`ed
  everywhere they're called) so it can be driven by FastAPI + async SQLAlchemy. This must be
  fully green (all existing domain/application tests passing with `pytest-asyncio`) before
  any infrastructure/presentation code is written. See the Phase 2 prompt / `TODO.md` for the
  exact sequencing.

Analytical sources for the original domain model: `domain-model.md`, `dbml-schema.md`,
`full-analysis.md`. If the current code contradicts these, `DOMAIN.md`/`APPLICATION.md` are
authoritative (they reflect what the code actually does) — only fall back to the raw
analysis files for genuinely undecided questions.

## 3. Strict Architectural Rules (Non-negotiable)

- **Dependency direction**: `presentation -> application -> domain` and
  `infrastructure -> application/domain`. `domain` has no imports from `application`,
  `infrastructure`, `presentation`, or `bootstrap`. `application` only imports `domain` +
  its own shared ports.
- **`presentation` never imports `infrastructure`, and vice versa.** These two packages are
  fully independent. The only package allowed to import both is `bootstrap/` (the
  Composition Root / "Main Component" — see `PRESENTATION.md` §3). `presentation` routers
  and dependencies only reference provider _stubs_ declared in
  `presentation/core/providers.py` (which raise `NotImplementedError` by default);
  `bootstrap/container.py` overrides them with real `infrastructure` implementations via
  `app.dependency_overrides`. Never import a concrete `infrastructure` class directly into
  a `presentation` router or dependency file, even "just this once".
- **No frameworks in `domain`/`application`**: no `import fastapi`, `import sqlalchemy`,
  `import pydantic`, etc. in these two layers (only `dataclasses`, `typing`, `abc`, `enum`,
  `datetime`, `uuid`, `asyncio` from the standard library).
- **Entities must not be Anemic**: business rules depending only on an Entity's own state
  live inside the Entity (e.g. `Project.assign_freelancer()` enforces the one-freelancer
  rule itself), not in the Use Case. The Use Case only orchestrates.
- **Repository Interfaces are in `domain`; implementations now belong in
  `infrastructure/repositories/`.** Every method on an interface — including ones not yet
  called by any use case — must be implemented; it is part of the contract.
- **Use Cases**: one input Command/Query DTO, one output Result DTO, one public
  `async def execute(...)` method (Command pattern). `actor_id` always comes from
  `get_current_user` in presentation, never from the request body.
- **Immutability where meaningful**: Value Objects and DTOs use `frozen=True` dataclass.
- **No duplicated Business Logic**: cross-cutting rules (revision cap, one-freelancer rule)
  live in a Domain Service (`domain/<context>/services.py`) and are called from every path
  that needs them — never copy-pasted into multiple Use Cases (this was a real bug found and
  fixed once in this codebase; do not reintroduce it).
- **Self vs. On-Behalf pattern (mandatory — full rationale in `AUTHORIZATION.md`)**:
  - _Pattern A_ — mutating/reading an existing owned entity where the owner is read from the
    loaded entity itself: ONE use case class using `authorize_owned_action(actor_id,
owner_id, "<res>.<action>_own", "<res>.<action>_any")`.
  - _Pattern B_ — creating a new entity that may be created "for" someone else (requires a
    new target-owner input field with no meaning in the self-service case): TWO thin use
    case classes (self-service + on-behalf), each checking exactly one permission, sharing
    core logic via a private helper function. The self-service Command DTO never gains a
    "target user" field.
  - Before adding any new owned-resource use case, check `AUTHORIZATION.md` for which
    pattern applies and for the list of entities where on-behalf is explicitly disallowed.
  - Any on-behalf creation path must verify the target user actually exists before creating
    anything, propagating `UserNotFoundError`/the equivalent lookup error if missing.
- **RBAC data-source contract (binding on Phase 2 infrastructure work)**: `PERMISSION_*`/
  role-key string constants in `application/` are identifiers only, corresponding to real
  rows in the `permissions`/`roles` tables. The real `IAuthorizationService` implementation
  (`infrastructure/security/authorization_service.py`) MUST resolve permission checks by
  querying `user_roles → role_permissions → permissions` — never a hardcoded
  `if role == "admin": return True` shortcut in Python. See `AUTHORIZATION.md` for the full
  binding text; this is the single most important correctness requirement of Phase 2.

## 4. Naming Conventions

- Files and packages: `snake_case`. Classes: `PascalCase`.
- Interfaces (Ports) prefixed `I`: `IUserRepository`, `ITokenService`.
- Exceptions suffixed `Error`, always inheriting the shared hierarchy in
  `ERROR_HANDLING.md`/`API_DESIGN.md`, never raw `Exception`.
- Use Cases suffixed `UseCase`; on-behalf variants prefixed `Admin...OnBehalfUseCase`.
- Command/Query DTOs suffixed `Command`/`Query`; on-behalf commands suffixed
  `OnBehalfCommand`. Result DTOs suffixed `Result`.
- Permission key constants: module-level `PERMISSION_<RESOURCE>_<ACTION>` (or `_OWN`/`_ANY`/
  `_ON_BEHALF` suffix for the two-tier convention) near the top of the use-case module.
- Enum values: `UPPER_SNAKE` members, DBML-aligned.
- IDs: `EntityId = str`, generated by `IIdGenerator`.
- Presentation provider stubs (`presentation/core/providers.py`): `get_<port_or_use_case>`,
  same name reused as the override key in `bootstrap/container.py` — never renamed between
  the two.

## 5. How the Agent Works on This Project

1. Before adding a new Entity/Use Case, check `DOMAIN.md`/`APPLICATION.md` to avoid
   duplication, and check `AUTHORIZATION.md` for which authorization pattern (A or B)
   applies.
2. For every new Entity, write its unit tests in the same commit (`TESTING.md`).
3. For every new Use Case (async):
   - Check required Repository/Service Interfaces; define them in `domain` first if
     missing.
   - Define Command/Result DTOs in `application/<context>/dto.py`.
   - Apply authorization first (`require_permission` or `authorize_owned_action`), then
     input validation, then mutate via the entity/domain service — in that order.
   - Write unit tests with async Fakes from `tests/fakes/`.
4. For every new `infrastructure` repository/service, implement the full interface (not
   just the methods currently called), test it against a real Postgres (no mocking
   SQLAlchemy), and never let a raw driver exception leak past its boundary — translate to a
   domain/application exception.
5. For every new `presentation` endpoint, follow the envelope/error/pagination conventions
   in `API_DESIGN.md` exactly, wire it through a provider stub (never import
   `infrastructure` directly), and build the Command from `get_current_user` + the request
   body per `PRESENTATION.md`.
6. After every change, update `TODO.md` and the relevant spec file(s).
7. Never take an architectural shortcut "just this once" (skipping an authorization check,
   importing infrastructure into presentation, hardcoding a permission decision) — these are
   exactly the classes of bugs this project has already had to retroactively fix once.
8. Running domain/application tests: `pytest -q` must pass without any external dependency.
   Running infrastructure tests requires a real Postgres (via `docker compose`).

## 6. Definition of Done

### Phase 1 (domain + application) — reference

- [x] All 9 bounded contexts implemented with Entities, Repository Interfaces, Use Cases.
- [x] Owned-resource authorization (`_own`/`_any`) and Self vs. On-Behalf pattern applied per
      `AUTHORIZATION.md`.
- [x] Test coverage on `domain`/`application` >= 90%; `mypy` clean; no forbidden imports.
- [ ] **Verify before Phase 2**: confirm with the person whether any previously-agreed
      authorization fixes (e.g. `CreateProject` self/on-behalf split, admin user CRUD) are
      fully applied in code and reflected in `DOMAIN.md`/`APPLICATION.md` — do not assume.

### Phase 2 (infrastructure + presentation + bootstrap) — current target

- [ ] `application` layer fully converted to async; all existing tests green under
      `pytest-asyncio`.
- [ ] `infrastructure` implements every Repository/Port interface from `domain`/
      `application`, per `INFRASTRUCTURE.md`.
- [ ] `presentation` exposes all endpoints per `PRESENTATION.md`/`API_DESIGN.md`, with zero
      `import app.infrastructure` anywhere under `presentation/` (verify with
      `grep -R "infrastructure" src/app/presentation`).
- [ ] `bootstrap/container.py` overrides every provider stub declared in
      `presentation/core/providers.py`.
- [ ] `docker compose up --build` succeeds: `migrate` exits 0, `app` becomes healthy,
      `GET /docs` loads, seeded admin can log in and `GET /api/v1/auth/me` shows correct
      `roles`/`permissions`.
- [ ] `IAuthorizationService` resolves permissions via a real DB join — verified by a test
      that revoking a permission in the DB changes the authorization outcome.
- [ ] Presentation and infrastructure test suites pass per `TESTING.md`'s extended rules;
      `domain`/`application` coverage has not regressed.

## 7. Tools and Versions

- Python >= 3.12
- pytest (latest stable), `pytest-cov`, `pytest-asyncio`, `pytest-mock`
- `mypy` (strict on `domain`/`application`; looser config acceptable for
  `infrastructure`/`presentation` if noted explicitly and justified)
- `ruff` for lint/format
- Dependency management: `pyproject.toml` (PEP 621)
- Phase 2 runtime dependencies: `fastapi`, `uvicorn[standard]`, `pydantic-settings`,
  `sqlalchemy[asyncio]>=2.0`, `asyncpg`, `alembic`, `pyjwt`, `argon2-cffi`
- Phase 2 dev/test dependencies: `httpx` (FastAPI TestClient)
- Docker + Docker Compose for local/staging environment (`postgres:16-alpine` + app image)

## 8. Common Commands

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run domain/application tests with coverage (no external services required)
pytest --cov=app/domain --cov=app/application --cov-report=term-missing

# Type check
mypy app/domain app/application

# Lint
ruff check app

# Bring up the full stack (db + migrate + seed + app)
docker compose up --build

# Generate a new Alembic migration after changing a SQLAlchemy model
alembic revision --autogenerate -m "description"

# Run the seed script standalone (idempotent — safe to re-run)
python -m app.infrastructure.seed.run_seed
```
