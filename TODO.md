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
  - New `file.upload`/`file.read_any` permissions seeded; `file.upload` granted to
    `customer` and `freelancer` roles.
  - Persistent storage backend implemented behind `IFileStorageService`:
    - `LocalDiskFileStorageService` (default, interim production backend) with streaming
      writes, size limits, and path-traversal-safe keys.
    - `S3FileStorageService` (configurable via `FILE_STORAGE_BACKEND=s3`).
  - `docker-compose.yml` includes a named volume for local storage; `Dockerfile` creates
    `/app/storage/files` owned by `appuser`.
  - Routes stream uploads and return actual file bytes via `StreamingResponse`.
  - End-to-end restart-survival test passed: upload → download matches, container restart,
    download again matches byte-for-byte.
  - Tests green (`tests/application`, `tests/presentation`), `ruff`, `mypy` clean.
- [x] **Part 4a** — Dedicated admin on-behalf routes: removed optional-body branching from
      `POST /projects` and `POST /projects/{id}/applications`; added `POST /admin/projects`,
      `POST /admin/projects/{id}/applications`, `POST /admin/freelancers`, `POST /admin/tickets`.
- [x] **Part 4b** — Freelancer admin/read gaps: approval-status listing, soft-delete, full
      `FreelancerLevel` CRUD, level history, resume read/rollback/delete, portfolio read.
- [x] **Part 4c** — Project read/access gaps: `GET /projects/{id}/applications/{application_id}`,
      `GET /projects/{id}/deliveries`, `GET /projects/{id}/revisions`,
      `GET /projects/{id}/status-history`, `GET /deliveries/{delivery_id}`,
      `GET /revisions/{revision_id}`, `POST /revisions/{revision_id}/close`.
- [x] **Part 4d** — Remaining review/feedback/ticketing/auth audit gaps from the audit table.
  - Review: `GET /deliveries/{delivery_id}/review`.
  - Feedback: `CustomerReview` read/list/update/delete, `Rating` update/delete, semantic
    ordering fix for `SubmitRating`.
  - Ticketing: `GET /tickets/{ticket_id}`, `PATCH /tickets/{ticket_id}` (subject/priority/status),
    `GET /tickets/{ticket_id}/participants`, `PATCH /DELETE /tickets/{ticket_id}/messages/{message_id}`.
- [x] **Part 5** — OpenAPI/presentation hygiene: tags, `summary`, error response examples,
      pagination follow-through.
  - `DocumentedAPIRoute` (`presentation/core/routes.py`) auto-generates `summary` from
    `operation_id` and merges default error responses (400/401/403/404/409/422/500) with
    `ErrorEnvelope` examples; wired as `route_class` on every HTTP router.
  - Shared `paginate()` helper + `PageQuery` on all 18 bare-list endpoints (project,
    freelancer, category, review, ticketing); removed duplicated `_pagination_meta`
    helpers. Verified: 130/130 operations have `summary` and a documented 400 response.
- [x] **Part 6** — IAM RBAC fix: `RemoveRole`/`RevokePermission` no longer gate link mutation
      on `is_system`. Because every seeded role has `is_system = True`, that guard rejected
      **every** call, so no role could be removed from a user and no permission revoked from a
      role. Replaced in `RemoveRole` with the real rule — the last active `admin` assignment
      cannot be removed (`LastAdminRoleRemovalError(InvalidStateTransitionError)` → HTTP 409);
      `RevokePermission` is now unrestricted (relationship configuration only).
      `SystemRoleImmutableError` retained but unraised, reserved for future catalog-entity
      (rename/delete) guards. Audited every other `is_system` read: `AssignRole` and
      `GrantPermission` correctly do not check it. Catalog-vs-link distinction documented in
      `docs/domain-usecases-documentation.md` §12.5.1.
- [x] **Part 7a** — Systemic soft-delete filtering (task §2). Every read path of the eight
      entities carrying `deleted_at` now filters `deleted_at IS NULL`; the Fakes mirror it so
      application tests catch leaks. Closed a live auth bypass: no `User` read filtered
      soft-deleted rows, so a deleted user could still log in via `get_by_email` and still
      appeared in admin lists/counts. `PortfolioItem` converted from HARD delete to true
      soft-delete (`PortfolioItem.soft_delete`, hard-delete repo method removed);
      `FormTemplate` had the same conflation (not in the brief) — its hard delete was also an
      FK/500 risk because terminal projects still hold `projects.form_template_id`, so it is
      soft-deleted now too; `ITicketMessageRepository.delete` (0 callers) removed for the same
      reason. No hard-delete repo method remains for any entity carrying `deleted_at`.
      `list_active_user_ids_for_role` now excludes soft-deleted admins so the last-admin
      guards can't be satisfied by a deleted account. Two documented exceptions:
      `email_exists_including_deleted` (mirrors the UNIQUE constraint) and
      `ticket_message.get_by_id` (mutation-only, keeps the entity's 409 guard reachable).
      Also fixed a pre-existing 500: `attachment_file_asset_ids`/`file_asset_ids` were `JSON`
      so the containment predicate compiled to an invalid `LIKE`, breaking file-access
      authorization — now `JSONB` (migration `a1c4e77b90d2`, upgrade+downgrade verified).
      New finding, not fixed: `TimestampMixin` timestamps are naive while iam/ticketing
      timestamps are tz-aware, and mixin-table repositories discard the entity's `created_at`.
      599 unit/presentation + 27 integration tests green; ruff + mypy clean.
- [x] **Part 7b** — Project DRAFT-only edit/delete (task §1). `Project.require_draft(action)`
      mirrors `FormTemplate.require_draft` and raises the new
      `ProjectNotDraftError(InvalidStateTransitionError)` → HTTP 409, whose message directs the
      caller to `CancelProject`; `Project.soft_delete(at)` and `Project.update_details(...)`
      both assert it. `UpdateProjectUseCase` (full-replacement of title/description/visibility/
      budget/priority/application_deadline/form_values, re-validating form values against the
      project's own template) and `DeleteProjectUseCase` (soft delete) are wired to
      `PATCH /projects/{id}` and `DELETE /projects/{id}` via `project.manage_own`/`manage_any`.
      `category_id` is never accepted from the client (derived from the template, see 7c);
      `form_template_id` is editable while a draft. No migration needed — `Project` already
      carried `deleted_at`. New finding, not fixed: `form_values` are
      validated then discarded system-wide (no form-value table exists), so the Dynamic Form
      Engine's output is never persisted.

- [x] **Part 7c** — Template-driven project creation + `ListFormTemplates` (task §3/§6).
      `GET /form-templates` lists templates across ALL categories (`?category_id=&status=&search=`
      + page/page_size) with SQL-level filtering and `PaginationMeta`, backed by new
      `IFormTemplateRepository.list_templates`/`count_templates` and
      `application/shared/pagination.py` (`limit_offset`/`total_pages`,
      `DEFAULT_PAGE_SIZE=20`, `MAX_PAGE_SIZE=100`). Project creation now takes
      `form_template_id` (Create/OnBehalf/Update); the category is DERIVED from
      `template.category_id` and never accepted from the client, so template and category can
      never disagree; non-PUBLISHED targets raise the new `FormTemplateNotPublishedError` (409).
      `UpdateProject` lets a draft switch templates and re-validates `form_values` against the
      new template. Fake repo updates (new methods, DTO shape changes) are out of scope per the
      tests-out-of-scope instruction — flagged for the final report, not applied.

- [x] **Part 7d** — Freelancer-level redesign to a fixed enum (task §5). The configurable
      `freelancer_levels` table and its FK columns are replaced by the closed
      `FreelancerLevelEnum` (JUNIOR / MID_LEVEL / SENIOR):
  - Domain: `FreelancerLevel` entity, `IFreelancerLevelRepository`,
    `FreelancerLevelNotFoundError`, and the level CRUD use cases (create/update/delete/
    activate/deactivate/list) are removed; `FreelancerProfile.current_level` and
    `FreelancerLevelHistory.old_level/new_level` are enum values; `Project.required_level`
    added and accepted by `update_details`.
  - Eligibility: `FreelancerEligibilityPolicy` rewritten — hierarchical `>=` (SENIOR may
    apply to any required level), `current_level is None` is ineligible when a level is
    required, no-required-level projects admit everyone, INVITE_ONLY always rejected,
    single global cap `MAX_ACTIVE_APPLICATIONS = 10` (per-level flags dropped). Applied in
    `ApplyForProject`, `AdminApplyForProjectOnBehalf`, and `GetAvailableProjects`, which now
    uses `IProjectRepository.list_available_for_freelancer(current_level)` with a DB-level
    hierarchical filter.
  - Approve: `ApproveFreelancer` no longer auto-grants a "standard" level or writes history;
    it just approves. `AssignFreelancerLevel` now assigns an enum value and always records
    history; `ListFreelancerLevelHistory` unchanged in shape.
  - Infrastructure: `FreelancerLevelModel` and `SqlAlchemyFreelancerLevelRepository` deleted;
    models/mappings/repositories switched to `current_level`/`old_level`/`new_level` string
    columns and `projects.required_level`; migration `3f9b1c2d5e8a` drops `freelancer_levels`
    and converts the FK columns (existing rows reset to NULL — admins re-assign; no data
    migration attempted, per §5 decision).
  - Presentation/DI: admin level-CRUD routes and providers removed; `AssignFreelancerLevel
    Request/Response` and history/profile schemas use enums; project create/on-behalf/update
    requests and responses expose `required_level`; `freelancer.manage_levels` permission and
    its seed row removed (`freelancer.assign_level` retained).
  - Verified: ruff clean, mypy clean (240 files), OpenAPI smoke — level-CRUD paths gone,
    `required_level` on project request/response schemas, enum-shaped level schemas. Migration
    file written but not executed (Docker unavailable); will be exercised on next
    `docker compose up`. Fake repo updates out of scope (tests-out-of-scope instruction) —
    flagged for the final report.

- [x] **Part 7e** — Two-party ticket redesign + `RelationshipEligibilityService` (task §8).
      Tickets are now strictly two-user conversations (creator + `target_user_id`); the
      participant model and assignment flow are removed entirely:
  - Domain: `TicketStatus` pruned to OPEN / CLOSED / ARCHIVED (removed `IN_PROGRESS`,
    `WAITING_*`, and with them `transition_to()`); `TicketParticipant` entity,
    `TicketParticipantRole`, and `ITicketParticipantRepository` removed; `Ticket` drops
    `assigned_to_user_id`/`assign()` in favour of required `target_user_id` + `is_party()`;
    `NotTicketParticipantError` → `NotTicketPartyError`; new `TicketRelationshipError`;
    new `RelationshipEligibilityService` (`domain/ticketing/services.py`) — project-anchored
    (both users stakeholders of the same project: customer / selected freelancer / assigned
    supervisor) or category-anchored (active category supervisor + stakeholder of a project in
    the category, or two supervisors); no anchor → rejected.
  - Application: `ensure_participant(repo, …)` → `ensure_party(ticket, actor)`; assign/
    list-participants use cases and DTOs removed; `CreateTicketCommand` requires
    `target_user_id`; `CreateTicketOnBehalfCommand` now takes `requester_user_id` +
    `target_user_id` (verifies both exist); create/on-behalf route through the relationship
    service; close is now party-agnostic (either party with `close_own`, or `close_any`);
    update-ticket statuses handled via close/archive/reopen; `PERMISSION_TICKET_ASSIGN`
    removed; `file_access_policy` checks `ticket.is_party`.
  - Infrastructure: `TicketModel` `assigned_to_user_id` → NOT NULL `target_user_id`;
    `TicketParticipantModel` and `SqlAlchemyTicketParticipantRepository` deleted;
    `list_for_user` filters creator OR target; migration `7e01b2c3d4e5` renames the column and
    drops `ticket_participants`; seed row `ticket.assign` removed.
  - Presentation: `/tickets/{ticket_id}/assign` and `/tickets/{ticket_id}/participants`
    routes removed; `TicketResponse`/`CreateTicketRequest`/`AdminCreateTicketRequest` updated;
    providers/container wired for the relationship service and unwired the participant repo.
  - Verified: ruff clean, mypy clean (239 files), OpenAPI smoke — 91 paths, no assign/
    participants routes, `target_user_id` on schemas, `TicketStatus` enum = open/closed/
    archived. Migration written but not executed (Docker unavailable). Fake repo updates out
    of scope (tests-out-of-scope instruction) — flagged for the final report.

- [x] **Part 7f** — Related-users picker for ticket creation (task §8).
      `GET /users/related` enumerates the users an actor has an eligible two-party ticket
      relationship with, mirroring `RelationshipEligibilityService`:
  - Domain: `RelatedUser` read model (`domain/ticketing/read_models.py`); `IRelatedUsersRepository`
    (`list_related_users(user_id, limit, offset)`, `count_related_users(user_id)`).
  - Application: `ListRelatedUsersQuery`/`ListRelatedUsersResult`/`RelatedUserResult` DTOs;
    `ListRelatedUsersUseCase` gated by `authorize_owned_action(ticket.read_own, ticket.read_any)`;
    DB-level pagination (7f, aligned with 7g).
  - Infrastructure: `SqlAlchemyRelatedUsersRepository` — UNION of project-anchored (customer /
    assigned supervisor / selected freelancer stakeholders, any project status) and
    category-anchored (co-active supervisors; supervisor + customer/selected-freelancer of open
    projects in a supervised category; active supervisors of categories where the user has an
    open project) subqueries; excludes self + soft-deleted users; ordered by `created_at desc`.
  - Presentation: `GET /api/v1/users/related` (`list_related_users`) in a dedicated router
    registered **before** the IAM `/users/{user_id}` route (so the literal `related` segment
    wins); `RelatedUserResponse` schema; `get_related_users_repository` +
    `get_list_related_users_use_case` provider stubs + container override.
  - Verified: ruff clean, mypy clean (241 files), OpenAPI smoke — 92 paths, `list_related_users`
    op_id, SQL subquery compiles. No migration needed (read-only query). Fake repo updates out
    of scope (tests-out-of-scope instruction) — flagged for the final report.

- [x] **Part 7g** — DB-level pagination on every remaining list endpoint (task §4). All 16
      client-side-slicing endpoints across project, category, freelancer (router + admin),
      ticketing, and review now page in SQL and return a real `PaginationMeta`, matching the
      pattern 7c established for `ListFormTemplates` via `application/shared/pagination.py`:
  - Pattern (uniform): list repo methods gain optional `limit`/`offset`
    (`limit: int | None = None, offset: int | None = None` — full list when omitted, so
    non-paged callers are untouched) plus a matching `count_*` method; use cases call
    `limit, offset = limit_offset(page, page_size)` and return `total_items`/`page`/`page_size`;
    routers pass `page=pagination.page, page_size=pagination.page_size` into the Query and
    build `PaginationMeta` with `total_pages=total_pages(total_items, page_size)`. The old
    in-memory `paginate()` helper in `presentation/core/pagination.py` was removed (no callers
    remain).
  - Project (6): `get_available_projects`, `get_my_projects`, `view_applications`,
    `list_project_deliveries`, `list_project_revision_requests`, `list_project_status_history`.
    New repo methods: `IProjectRepository.list_by_customer`/`list_available_for_freelancer`/
    `list_by_supervisor`/`list_by_category` + `count_by_customer`/`count_available_for_freelancer`/
    `count_by_supervisor`/`count_open_by_category` (a new method — `count_active_by_category`
    counts non-terminal statuses while `list_by_category` returns only open ones, so reusing it
    would corrupt `total_items`); `IProjectApplicationRepository`/`IProjectDeliveryRepository`/
    `IProjectStatusHistoryRepository` list_by_project + count_by_project;
    `IProjectRevisionRequestRepository` list_by_project (count_by_project already existed).
  - Category (2): `get_categories` (`ICategoryRepository.list_active` + `count_active`),
    `get_category_projects` (`list_by_category` + `count_open_by_category`).
  - Freelancer (4): `list_freelancer_profiles_by_approval_status`
    (`IFreelancerProfileRepository.list_by_approval_status` + `count_by_approval_status`),
    `list_resume_versions`, `list_portfolio_items`, `list_freelancer_level_history`
    (each `list_by_profile` + `count_by_profile` on the respective repo).
    `resume_repository.list_by_profile` ordering changed from `version_no.desc()` to
    `version_no.asc()` — the list use case previously sorted ascending in-memory, which is
    incompatible with DB paging; the other callers (`upload_resume` max, `set_current_resume`
    iterate, `delete_resume` next) are order-agnostic.
  - Ticketing (2): `get_user_tickets` (`ITicketRepository.list_for_user` + `count_for_user`),
    `get_ticket_messages` (`ITicketMessageRepository.list_by_ticket` + `count_by_ticket`).
  - Review (2): `get_pending_reviews`
    (`ISupervisorReviewRepository.list_pending_for_supervisor` + `count_pending_for_supervisor`),
    `get_supervisor_projects` (`list_by_supervisor` + `count_by_supervisor`).
  - DTOs: every list Query defaults `page_size: int = DEFAULT_PAGE_SIZE` (was `20`); every list
    Result carries `total_items`/`page`/`page_size`.
  - Verified: ruff clean, mypy clean (241 files), OpenAPI smoke — 92 paths, all 18 list op_ids
    present with `page`/`page_size` params, no inline offset/total_pages math left in
    `src/app`. No migration needed (read-path changes only). Fake repo updates out of scope
    (tests-out-of-scope instruction) — flagged for the final report; `test_pagination.py`
    line 102 (`page=99` clamps to `page: 3`) encodes the old in-memory clamping behaviour and
    will need updating for the new DB-paging semantics.
