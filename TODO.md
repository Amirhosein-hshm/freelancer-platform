# TODO.md — Phase 2 Checklist (infrastructure + presentation + bootstrap + docker)

Phase 1 (`domain` + `application`, including authorization hardening and admin IAM CRUD) is
functionally complete. This checklist covers Phase 2 only. Check items as they are verified
green (tests passing), not just "code written".

## Phase 2, Step 0 — Verify Phase 1 state before starting

- [x] `CreateProject` self-service/on-behalf split (`Project.created_by_user_id`,
      `CreateProjectOnBehalfCommand`, `AdminCreateProjectOnBehalfUseCase`) is implemented
      and verified; `DOMAIN.md` updated to match.
- [x] Same check, all confirmed implemented and covered by tests:
      `AdminCreateUserUseCase`/`AdminUpdateUserUseCase`/`AdminDeleteUserUseCase` +
      `CannotDeleteSelfError`/`LastAdminCannotBeDeletedError`;
      `AdminApplyForProjectOnBehalfUseCase`; `AdminCreateFreelancerProfileOnBehalfUseCase`;
      `AdminCreateTicketOnBehalfUseCase`; `CustomerReviewNotApprovedError` in
      `SubmitRatingUseCase`; `IUserRoleRepository.list_active_user_ids_for_role`.
- [x] No remaining Phase 1 correctness gaps found — all closed before proceeding.

## Phase 2, Step 1 — Async conversion (blocking prerequisite)

- [x] `application/shared/use_case.py`: `UseCase.execute` -> `async def execute`.
- [x] Every use case's `execute` -> `async def execute`; every repository/port call inside
      is `await`ed.
- [x] Every port in `application/shared/ports.py` and every repository interface in
      `domain/*/repositories.py`: methods -> `async def`; `IUnitOfWork` ->
      `__aenter__`/`__aexit__`.
- [x] Every Fake in `tests/fakes/` updated to async.
- [x] Every test in `tests/application/**` -> `async def test_...`;
      `asyncio_mode = "auto"` added to `pyproject.toml`.
- [x] Full domain+application test suite green under `pytest-asyncio` before continuing.

## Phase 2, Step 2 — Infrastructure

- [ ] `config.py` (`Settings` via `pydantic-settings`).
- [ ] `db/base.py`, `db/session.py`, `db/unit_of_work.py`.
- [ ] `db/models/*.py` — one SQLAlchemy model group per bounded context.
- [ ] `repositories/*.py` — full implementation of every interface listed in
      `ARCHITECTURE.md` §5.1 (including methods not yet called by any use case).
- [ ] `security/password_hasher.py` (Argon2), `security/token_service.py` (PyJWT),
      `security/authorization_service.py` (real DB join — verified against
      `AUTHORIZATION.md` §6 contract).
- [ ] `notifications/websocket_notification_service.py` + new `IRealtimeNotifier` port.
- [ ] `clock.py`, `id_generator.py`, `code_generators.py` (atomic, race-free).
- [ ] Alembic initialized; initial migration covers every model.
- [ ] `seed/seed_data.py`, `seed/run_seed.py` — idempotent; every `PERMISSION_*` constant
      across `application/` cross-checked against seed data; admin bootstrap from env vars.

## Phase 2, Step 3 — Presentation

- [ ] `core/envelope.py`, `core/error_handlers.py`, `core/security.py`,
      `core/providers.py` (stubs only — zero infrastructure imports), `core/pagination.py`.
- [ ] Admin IAM read endpoints (`GET /users`, `GET /users/{user_id}`) added with the
      `user.read` permission (seeded) and **real DB offset/limit pagination** on
      `GET /users` (`IUserRepository.list_all`/`list_by_status` + `count_all`) — the partial
      fix for the fake-pagination gap in `docs/presentation-analysis.md` §7 item 2; the other
      paginated list endpoints (projects, reviews) still slice client-side and should be
      migrated to this pattern.
- [ ] `websocket/connection_manager.py`, `websocket/router.py`.
- [ ] `api/v1/<context>/router.py` + `schemas.py` for all 9 contexts + `api/v1/auth/`.
- [ ] Every endpoint: explicit `response_model`, `operation_id`, `tags`, documented error
      responses.
- [ ] `main.py` — `create_app()`, routers, exception handlers, CORS, request-id middleware.
- [ ] `grep -R "infrastructure" src/app/presentation` returns no real imports.

## Phase 2, Step 4 — Tests

- [ ] Infrastructure tests against a real Postgres (`@pytest.mark.integration`), per
      `TESTING.md` §8, including the RBAC data-source contract test.
- [ ] Presentation tests via `TestClient` + `dependency_overrides`, per `TESTING.md` §9.
- [ ] `tests/domain/`/`tests/application/` still green throughout.

## Phase 2, Step 5 — Bootstrap & Docker

- [x] `bootstrap/container.py` overrides every provider stub; `bootstrap/run.py` entrypoint.
- [x] `Dockerfile` (multi-stage, non-root `appuser`), CMD points at `app.bootstrap.run:app`.
- [x] `docker-compose.yml` (`db` with healthcheck, one-shot `migrate`, `app` depending on
      `migrate` completing).
- [x] `.env.example`, `.dockerignore`, `.gitignore` includes `.env`.
- [ ] `docker compose up --build` succeeds end-to-end: `migrate` exits 0, `app` healthy,
      `/docs` loads, seeded admin can log in, `/api/v1/auth/me` shows correct
      roles/permissions. (Files written and compose config validated; full E2E blocked
      on Docker Hub network access.)
- [x] README "Getting Started" section added.

## Phase 2, Step 6 — Wrap-up

- [ ] `pytest --cov=app/domain --cov=app/application --cov-report=term-missing
    --cov-fail-under=90` still passing.
- [ ] `mypy app/domain app/application` clean.
- [ ] `ruff check app` clean.
- [ ] `ARCHITECTURE.md`, `DOMAIN.md`, `APPLICATION.md`, `AUTHORIZATION.md` updated for any
      new field/exception/interface discovered during implementation.
- [ ] This file's checkboxes all checked.

## CRUD/Presentation Audit Remediation (Parts 1–5)

- [x] **Part 1** — Audit all Phase-1 presentation endpoints against implemented use cases;
      read-only catalog endpoints `GET /roles` and `GET /permissions` implemented
      (`user.read` permission); docs updated.
- [x] **Part 2** — Category/Form integrity:
  - `DeleteCategoryUseCase` guards against child categories and active projects.
  - `GetCategoryUseCase`, `ListCategorySupervisorsUseCase` + public routes.
  - `GetFormTemplateByIdUseCase` fixes `/form-templates/{template_id}` route bug.
  - `ListFormTemplateVersionsUseCase`, `DeleteFormTemplateUseCase`,
    `UpdateFieldOptionUseCase`, `RemoveFieldOptionUseCase`.
  - `FormField` option domain methods; `ReferencedEntityConflictError` → HTTP 409.
  - Tests green (`tests/application`, `tests/presentation`), `ruff`, `mypy` clean.
- [x] **Part 3** — File upload subsystem:
  - `POST /files` with content-derived MIME validation (`filetype`) and server-generated asset IDs.
  - `GET /files/{file_asset_id}` with context-aware authorization (`IFileAccessPolicy`).
  - File-existence checks added to `AddPortfolioItemUseCase`, `UpdatePortfolioItemUseCase`,
    `SubmitDeliveryUseCase`, and `SendMessageUseCase`.
  - New `file.upload`/`file.read_any` permissions seeded.
  - End-to-end tests for all four consumers + file routes; `ruff`, `mypy` clean.
- [ ] **Part 4** — On-behalf admin routes: implement missing on-behalf creation/mutation paths
      from audit table.
- [ ] **Part 4** — On-behalf admin routes: implement missing on-behalf creation/mutation paths
      from audit table.
- [ ] **Part 5** — OpenAPI/presentation hygiene: tags, `summary`, error response examples,
      pagination follow-through.
