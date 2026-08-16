# Presentation Layer Analysis — Freelance / Project Platform

> **Scope:** `src/app/presentation/**` (FastAPI routers, Pydantic schemas, DI provider
> stubs, envelope/error-handlers, WebSocket) plus how it drives the `application` layer
> and the API contracts it must satisfy (`API_DESIGN.md`, `PRESENTATION.md`,
> `ERROR_HANDLING.md`).
> **Method:** every route, operation_id, status code, and DTO mapping below was read
> directly from the implementation (`file:line` references included).
> **Prerequisite reading:** `docs/domain-usecases-documentation.md` describes the
> underlying domain & use cases; this document focuses on the web layer.

---

## Table of Contents

1. [Overview](#1-overview)
2. [File-by-File Breakdown](#2-file-by-file-breakdown)
3. [Route-by-Route Documentation](#3-route-by-route-documentation)
4. [Domain & Use-Case Extraction](#4-domain--use-case-extraction)
5. [Envelope & Error Contracts](#5-envelope--error-contracts)
6. [Cross-File Consistency](#6-cross-file-consistency)
7. [Critical Gaps & Inconsistencies](#7-critical-gaps--inconsistencies)
8. [Summary & Score](#8-summary--score)

---

## 1. Overview

### 1.1 What this layer is

The "presentation/project" under analysis is the **FastAPI web layer** of a freelance /
project-micro-job marketplace backend. There are **no slides, PPTX, or image assets** in
the repository — the term maps to:

- `src/app/presentation/` — the running HTTP surface: 11 versioned routers + 1 WebSocket,
  request/response schemas, the response envelope, the global exception handlers, the
  bearer-token auth dependency, and the DI provider stubs.
- `src/app/infrastructure/` + `src/app/bootstrap/container.py` — the Composition Root that
  wires real implementations into the stubs (not part of this analysis, referenced only
  where they explain seams).
- `src/app/application/**` — the Use Cases / DTOs the routers call (referenced with line refs where relevant).

### 1.2 Architecture rules honored by the implementation

| Rule (`ARCHITECTURE.md`/`AGENTS.md`) | Verified status |
|---|---|
| `presentation` never imports `infrastructure` | ✅ verified (grep in §6.1) |
| Routers only import `application` types + provider stubs | ✅ |
| `bootstrap/container.py` is the only place importing both | ✅ |
| `actor_id` always from `get_current_user`, never the body | mostly ✅ (the only body-IDs are target/owner IDs, not actor) |
| Response envelope wraps every success payload | ✅ |
| Every error maps through `register_exception_handlers` | ✅ |

### 1.3 Status line

- **Phase status:** domain + application fully implemented (Phase 1 ✅); the presentation
  layer is **implemented but may have incomplete spots** — a dynamic "build," see §7.

---

## 2. File-by-File Breakdown

### 2.1 Root / wiring

| File | Responsibility |
|---|---|
| `src/app/presentation/main.py` | `create_app()` — builds `FastAPI`, registers all routers under `API_PREFIX = "/api/v1"`, registers exception handlers. **WS not prefixed** (mounted separately). |
| `src/app/presentation/api/v1/*/router.py` | One `APIRouter` per bounded context (see §3). |
| `src/app/presentation/api/v1/*/schemas.py` | Pydantic request/response models per context. |
| `src/app/presentation/core/envelope.py` | `SuccessEnvelope[T]`, `ErrorEnvelope`, `ErrorDetail`, `PaginationMeta`. |
| `src/app/presentation/core/error_handlers.py` | Global exception handler registration, `_envelope` serializer, `to_error_code`. |
| `src/app/presentation/core/pagination.py` | `PageQuery` (`page`/`page_size` query params). |
| `src/app/presentation/core/security.py` | `get_current_user` (Bearer token → `ITokenService.decode_access_token`). |
| `src/app/presentation/core/providers.py` | DI **stubs** for every repository, port, and use case (raise `NotImplementedError`). |
| `src/app/presentation/websocket/router.py` | WebSocket `/ws/notifications` route (token-in-query). |
| `src/app/presentation/websocket/connection_manager.py` | In-memory WebSocket connection registry. |
| `src/app/presentation/README.md` | ⚠️ **Stale** (see §7.2) — claims the package is "intentionally empty". |

### 2.2 Schema location conventions

- Request models end `Request`; response models end `Response`; both use `Pydantic`
  `BaseModel`. Domain enums are reused directly in request/response models (e.g.
  `ProjectVisibility`, `ReviewStatus`), which keeps enum strings aligned DB-side.
- Note: responses are **not** the `application` Result DTOs — router code maps
  `Result` → Pydantic response explicitly in each handler extension.

---

## 3. Route-by-Route Documentation

All prefix/paths below are appended to `API_PREFIX = "/api/v1"` unless marked `(WS)`.
`auth` = requires `get_current_user` (Bearer token). A few endpoints are public.

### 3.1 Auth — `/api/v1/auth`

| # | Method | Path | op_id | Auth | Request → Use Case |
|---|---|---|---|---|---|
| 1 | POST | `/auth/register` | `register_user` | public | `RegisterUserCommand` → `RegisterUserUseCase` |
| 2 | POST | `/auth/login` | `login_user` | public | `LoginUserCommand` → `LoginUserUseCase` |
| 3 | POST | `/auth/refresh` | `refresh_token` | public | `RefreshTokenCommand` → `RefreshTokenUseCase` |
| 4 | POST | `/auth/logout` | `logout` | public | `LogoutUserCommand` → `LogoutUserUseCase` |
| 5 | POST | `/auth/change-password` | `change_password` | auth | `ChangePasswordCommand` → `ChangePasswordUseCase` |
| 6 | POST | `/auth/forgot-password` | `forgot_password` | public | `ForgotPasswordCommand` → `ForgotPasswordUseCase` |
| 7 | GET | `/auth/me` | `get_me` | auth | reads `IUserRepository.get_by_id` + `list_permissions_for_user` |

**Route → use-case mapping notes**
- `/auth/me` calls the **repository directly** in the handler (not a use case), and
  `authorization_service.list_permissions_for_user` to populate `permissions`.

### 3.2 IAM Admin — `/api/v1/users`

| # | Method | Path | op_id | Auth | Request → Response |
|---|---|---|---|---|---|
| 8 | POST | `/users` | `admin_create_user` | auth | `AdminCreateUserCommand` → `AdminCreateUserUseCase` (201) |
| 9 | PATCH | `/users/{user_id}` | `admin_update_user` | auth | `AdminUpdateUserCommand` → `AdminUpdateUserUseCase` |
| 10 | DELETE | `/users/{user_id}` | `admin_delete_user` | auth | `AdminDeleteUserCommand` → `AdminDeleteUserUseCase` |
| 11 | POST | `/users/{user_id}/activate` | `activate_user` | auth | `ActivateUserCommand` → `ActivateUserUseCase` |
| 12 | POST | `/users/{user_id}/block` | `block_user` | auth | `BlockUserCommand` → `BlockUserUseCase` |
| 13 | POST | `/users/{user_id}/roles` | `assign_role` | auth | `AssignRoleCommand` → `AssignRoleUseCase` |
| 14 | DELETE | `/users/{user_id}/roles/{role_key}` | `remove_role` | auth | `RemoveRoleCommand` → `RemoveRoleUseCase` |
| 15 | POST | `/users/roles/{role_id}/permissions` | `grant_permission` | auth | `GrantPermissionCommand` → `GrantPermissionUseCase` |
| 16 | DELETE | `/users/roles/{role_id}/permissions/{permission_id}` | `revoke_permission` | auth | `RevokePermissionCommand` → `RevokePermissionUseCase` |
| 17 | GET | `/users` | `admin_list_users` | auth | `AdminListUsersQuery` → `AdminListUsersUseCase` — **real DB offset/limit + `count_all` total** (partial fix of §7 item 2; only this endpoint paginates server-side) |
| 18 | GET | `/users/{user_id}` | `admin_get_user` | auth | `AdminGetUserQuery` → `AdminGetUserUseCase` (includes active `roles`) |

### 3.2a IAM Catalog — `/api/v1`

Read-only surfacing of the seeded role and permission catalogs. Both require `user.read`.

| # | Method | Path | op_id | Auth | Request → Response |
|---|---|---|---|---|---|
| 18a | GET | `/roles` | `list_roles` | auth | `ListRolesQuery` → `ListRolesUseCase` |
| 18b | GET | `/permissions` | `list_permissions` | auth | `ListPermissionsQuery` → `ListPermissionsUseCase` (optional `?module=` filter) |

### 3.3 Category — `/api/v1/categories`

| # | Method | Path | op_id | Auth | Request → Response |
|---|---|---|---|---|---|
| 19 | GET | `/categories` | `get_categories` | **public** | `GetCategoriesQuery` → `GetCategoriesUseCase` |
| 20 | GET | `/categories/{category_id}/projects` | `get_category_projects` | auth | `GetCategoryProjectsQuery` → `GetCategoryProjectsUseCase` |
| 21 | POST | `/categories` | `create_category` | auth | `CreateCategoryCommand` → `CreateCategoryUseCase` (201) |
| 22 | PATCH | `/categories/{category_id}` | `update_category` | auth | `UpdateCategoryCommand` → `UpdateCategoryUseCase` |
| 23 | DELETE | `/categories/{category_id}` | `delete_category` | auth | `DeleteCategoryCommand` → `DeleteCategoryUseCase` |
| 24 | POST | `/categories/{category_id}/supervisors` | `assign_supervisor` | auth | `AssignSupervisorCommand` → `AssignSupervisorUseCase` |
| 25 | DELETE | `/categories/{category_id}/supervisors/{supervisor_user_id}` | `remove_supervisor` | auth | `RemoveSupervisorCommand` → `RemoveSupervisorUseCase` |

### 3.4 Form Engine — `/api/v1/form-templates`

| # | Method | Path | op_id | Auth | Request → Response |
|---|---|---|---|---|---|
| 26 | POST | `/form-templates` | `create_form_template` | auth | `CreateFormTemplateCommand` → `CreateFormTemplateUseCase` (201) |
| 27 | **GET** | `/form-templates/{template_id}` | `get_form_template` | auth | ⚠️ `GetFormTemplateQuery(category_id=template_id)` — **see bug in §7.1** |
| 28 | PATCH | `/form-templates/{template_id}` | `update_form_template` | auth | `UpdateFormTemplateCommand` → `UpdateFormTemplateUseCase` |
| 29 | POST | `/form-templates/{template_id}/publish` | `publish_form_template` | auth | `PublishFormTemplateCommand` → `PublishFormTemplateUseCase` |
| 30 | POST | `/form-templates/{template_id}/fields` | `add_field` | auth | `AddFieldCommand` → `AddFieldUseCase` (201) |
| 31 | PATCH | `/form-templates/{template_id}/fields/{field_id}` | `update_field` | auth | `UpdateFieldCommand` → `UpdateFieldUseCase` |
| 32 | DELETE | `/form-templates/{template_id}/fields/{field_id}` | `remove_field` | auth | `RemoveFieldCommand` → `RemoveFieldUseCase` |
| 33 | POST | `/form-templates/{template_id}/fields/{field_id}/options` | `add_field_option` | auth | `AddFieldOptionCommand` → `AddFieldOptionUseCase` (201) |

### 3.5 Freelancer — `/api/v1/freelancers`

| # | Method | Path | op_id | Auth | Request → Response |
|---|---|---|---|---|---|
| 34 | GET | `/freelancers/{profile_id}` | `get_freelancer_profile` | auth | `GetFreelancerProfileQuery` → `GetFreelancerProfileUseCase` |
| 35 | POST | `/freelancers` | `create_freelancer_profile` | auth | `CreateFreelancerProfileCommand` → `CreateFreelancerProfileUseCase` (201) |
| 36 | PATCH | `/freelancers/{profile_id}` | `update_freelancer_profile` | auth | `UpdateFreelancerProfileCommand` → `UpdateFreelancerProfileUseCase` |
| 37 | POST | `/freelancers/{profile_id}/submit-approval` | `submit_freelancer_approval` | auth | `SubmitFreelancerApprovalCommand` → `SubmitFreelancerApprovalUseCase` |
| 38 | POST | `/freelancers/{profile_id}/approve` | `approve_freelancer` | auth | `ApproveFreelancerCommand` → `ApproveFreelancerUseCase` |
| 39 | POST | `/freelancers/{profile_id}/reject` | `reject_freelancer` | auth | `RejectFreelancerCommand` → `RejectFreelancerUseCase` |
| 40 | POST | `/freelancers/{profile_id}/level` | `assign_freelancer_level` | auth | `AssignFreelancerLevelCommand` → `AssignFreelancerLevelUseCase` |
| 41 | POST | `/freelancers/{profile_id}/resume` | `upload_resume` | auth | `UploadResumeCommand` → `UploadResumeUseCase` (201) |
| 42 | PATCH | `/freelancers/{profile_id}/resume` | `update_resume` | auth | `UpdateResumeCommand` → `UpdateResumeUseCase` |
| 43 | POST | `/freelancers/{profile_id}/portfolio` | `add_portfolio_item` | auth | `AddPortfolioItemCommand` → `AddPortfolioItemUseCase` (201) |
| 44 | PATCH | `/freelancers/{profile_id}/portfolio/{item_id}` | `update_portfolio_item` | auth | `UpdatePortfolioItemCommand` → `UpdatePortfolioItemUseCase` |
| 45 | DELETE | `/freelancers/{profile_id}/portfolio/{item_id}` | `delete_portfolio_item` | auth | `DeletePortfolioItemCommand` → `DeletePortfolioItemUseCase` |

### 3.6 Project (core) — `/api/v1/projects`

| # | Method | Path | op_id | Auth | Request → Response |
|---|---|---|---|---|---|
| 46 | POST | `/projects` | `create_project` | auth | self OR on-behalf (`CreateProjectOnBehalfCommand` when `customer_user_id`) → `CreateProjectUseCase` / `AdminCreateProjectOnBehalfUseCase` (201) |
| 47 | GET | `/projects` | `get_available_projects` | auth (freelancer) | `GetAvailableProjectsQuery` → `GetAvailableProjectsUseCase` `total_pages` meta built from returned list length |
| 48 | GET | `/projects/my` | `get_my_projects` | auth | `GetMyProjectsQuery` → `GetMyProjectsUseCase` |
| 49 | GET | `/projects/{project_id}` | `get_project_details` | auth | `GetProjectDetailsQuery` → `GetProjectDetailsUseCase` |
| 50 | POST | `/projects/{project_id}/publish` | `publish_project` | auth | `PublishProjectCommand` → `PublishProjectUseCase` |
| 51 | POST | `/projects/{project_id}/cancel` | `cancel_project` | auth | `CancelProjectCommand` → `CancelProjectUseCase` |
| 52 | POST | `/projects/{project_id}/complete` | `complete_project` | auth | `CompleteProjectCommand` → `CompleteProjectUseCase` |
| 53 | POST | `/projects/{project_id}/applications` | `apply_for_project` | auth | self OR on-behalf (`AdminApplyForProjectOnBehalfCommand`) (201) |
| 54 | GET | `/projects/{project_id}/applications` | `view_applications` | auth | `ViewApplicationsQuery` → `ViewApplicationsUseCase` |
| 55 | POST | `/projects/{project_id}/applications/{application_id}/accept` | `accept_freelancer` | auth | `AcceptFreelancerCommand` → `AcceptFreelancerUseCase` |
| 56 | POST | `/projects/{project_id}/applications/{application_id}/reject` | `reject_freelancer_application` | auth | `RejectFreelancerCommand` → `RejectFreelancerUseCase` |
| 57 | POST | `/projects/{project_id}/applications/{application_id}/withdraw` | `withdraw_application` | auth | `WithdrawApplicationCommand` → `WithdrawApplicationUseCase` |
| 58 | POST | `/projects/{project_id}/start` | `start_project` | auth | `StartProjectCommand` → `StartProjectUseCase` |
| 59 | POST | `/projects/{project_id}/deliveries` | `submit_delivery` | auth | `SubmitDeliveryCommand` → `SubmitDeliveryUseCase` (201) |
| 60 | POST | `/projects/{project_id}/revisions` | `request_revision` | auth | `RequestRevisionCommand` → `RequestRevisionUseCase` |

### 3.7 Review — `/api/v1/reviews` + `/api/v1/deliveries`

| # | Method | Path | op_id | Auth | Request → Response |
|---|---|---|---|---|---|
| 62 | GET | `/reviews/pending` | `get_pending_reviews` | auth (supervisor) | `GetPendingReviewsQuery` → `GetPendingReviewsUseCase` |
| 63 | GET | `/reviews/supervisor/projects` | `get_supervisor_projects` | auth | `GetSupervisorProjectsQuery` → `GetSupervisorProjectsUseCase` |
| 64 | POST | `/deliveries/{delivery_id}/review` | `review_delivery` | auth | `ReviewDeliveryCommand` → `ReviewDeliveryUseCase` |
| 65 | POST | `/deliveries/{delivery_id}/approve` | `approve_delivery` | auth | `ApproveDeliveryCommand` → `ApproveDeliveryUseCase` |
| 66 | POST | `/deliveries/{delivery_id}/reject` | `reject_delivery` | auth | `RejectDeliveryCommand` → `RejectDeliveryUseCase` |

### 3.8 Feedback — `/api/v1/feedback`

| # | Method | Path | op_id | Auth | Request → Response |
|---|---|---|---|---|---|
| 67 | POST | `/feedback/reviews` | `submit_review` | auth | `SubmitReviewCommand` → `SubmitReviewUseCase` (201) |
| 68 | POST | `/feedback/ratings` | `submit_rating` | auth | `SubmitRatingCommand` → `SubmitRatingUseCase` (201) |
| 69 | GET | `/feedback/projects/{project_id}/rating` | `get_project_rating` | auth | `GetProjectRatingQuery` → `GetProjectRatingUseCase` |
| 70 | GET | `/feedback/freelancers/{freelancer_profile_id}/ratings` | `get_freelancer_ratings` | auth | `GetFreelancerRatingsQuery` → `GetFreelancerRatingsUseCase` |

### 3.9 Ticketing — `/api/v1/tickets`

| # | Method | Path | op_id | Auth | Request → Response |
|---|---|---|---|---|---|
| 71 | POST | `/tickets` | `create_ticket` | auth | `CreateTicketCommand` → `CreateTicketUseCase` (201) |
| 72 | GET | `/tickets` | `get_user_tickets` | auth | `GetUserTicketsQuery` → `GetUserTicketsUseCase` |
| 73 | GET | `/tickets/{ticket_id}/messages` | `get_ticket_messages` | auth | `GetTicketMessagesQuery` → `GetTicketMessagesUseCase` |
| 74 | POST | `/tickets/{ticket_id}/messages` | `send_message` | auth | `SendMessageCommand` → `SendMessageUseCase` (201) |
| 75 | POST | `/tickets/{ticket_id}/assign` | `assign_ticket` | auth | `AssignTicketCommand` → `AssignTicketUseCase` |
| 76 | POST | `/tickets/{ticket_id}/close` | `close_ticket` | auth | `CloseTicketCommand` → `CloseTicketUseCase` |

### 3.10 Reporting — `/api/v1/reporting`

| # | Method | Path | op_id | Auth | Request → Response |
|---|---|---|---|---|---|
| 77 | GET | `/reporting/dashboard` | `get_dashboard_statistics` | auth | `ReportingQuery` → `GetDashboardStatisticsUseCase` |
| 78 | GET | `/reporting/users` | `get_user_statistics` | auth | `ReportingQuery` → `GetUserStatisticsUseCase` |
| 79 | GET | `/reporting/projects` | `get_project_statistics` | auth | `ReportingQuery` → `GetProjectStatisticsUseCase` |
| 80 | GET | `/reporting/freelancers` | `get_freelancer_statistics` | auth | `ReportingQuery` → `GetFreelancerStatisticsUseCase` |
| 81 | GET | `/reporting/customers` | `get_customer_statistics` | auth | `ReportingQuery` → `GetCustomerStatisticsUseCase` |
| 82 | GET | `/reporting/system-analytics` | `get_system_analytics` | auth (admin) | `ReportingQuery` → `GetSystemAnalyticsUseCase` |

### 3.11 WebSocket — `/ws/notifications` (NOT under `/api/v1`)

| # | Type | Path | Auth | Notes |
|---|---|---|---|---|
| 83 | WS | `/ws/notifications` | token via **query param** `?token=` | `decode_access_token` → `manager.connect` → echo loop → disconnect; **errors are not handled** (see §7) |

---

## 4. Use-Case Extraction (Presentation → Application Mapping)

Every router handler constructs the application Command/Query, executes the UseCase, then
maps the `Result` → Pydantic response. Consistent pattern: **one handler = one use case**
(with `# auth` subtleties calling out multi-use-case endpoints).

| Presentation concern | Use Case(s) driven | Cross-boundary notes |
|---|---|---|
| `POST /projects` | `CreateProjectUseCase` (self) OR `AdminCreateProjectOnBehalfUseCase` | The handler **branches** on `payload.customer_user_id` — both `create_kwargs` with `actor_id` (from token) and the `customer_user_id` go to the OnBehalfCommand; the self command carries no owner field. Deviation from a strictly-hot single command path — **flag**. |
| `POST /projects/{id}/applications` | `ApplyForProjectUseCase` OR `AdminApplyForProjectOnBehalfUseCase` | Branches on `target_freelancer_profile_id`. Same dual-path pattern. |
| `GET /auth/me` | none — direct repo + authz reads | Only endpoint calling `user_repo` + `list_permissions_for_user` directly. |
| `GET /projects` | `GetAvailableProjectsUseCase` | Requires a freelancer profile; returns projects per level. Pagination meta computed from the in-memory list length — **no real DB pagination** (see §7). |
| `GET /users` | `AdminListUsersUseCase` | Only list endpoint (currently) with **real DB offset/limit + `count_all` total** — the reference fix for §7 item 2. |
| All reporting GETs | `GetXStatisticsUseCase` | `ReportingQuery(actor_id)` reused for all — coarse (no filters). |

---

## 5. Envelope & Error Contracts

### 5.1 Envelope

- `SuccessEnvelope[T]` (`core/envelope.py:15`): `{"success": true, "message": str, "data": T, "meta": PaginationMeta | None}`.
- `ErrorEnvelope` (`core/envelope.py:36`): `{"success": false, "error": {"code", "message", "details"}}`.
- `PaginationMeta` (`core/envelope.py:8`): `{page, page_size, total_items, total_pages}`.
- ✅ matches `API_DESIGN.md`.

### 5.2 Status-code mapping (`core/error_handlers.py`)

| Exception | HTTP | Code derivation |
|---|---|---|
| `EntityNotFoundError` | 404 | `to_error_code` → `ENTITY_NOT_FOUND` |
| `InvalidStateTransitionError` | 409 | `INVALID_STATE_TRANSITION` |
| `BusinessRuleViolationError` | 422 | `BUSINESS_RULE_VIOLATION` |
| `UniqueConstraintViolationError` | 409 | `UNIQUE_CONSTRAINT_VIOLATION` |
| `PermissionDeniedError` | 403 | `PERMISSION_DENIED` |
| `ValidationError` | 400 | `VALIDATION` |
| `ExternalServiceError` | 502 | `EXTERNAL_SERVICE` |
| Bearer-token auth failures (`Invalid/ExpiredTokenError` via `get_current_user`) | 401 HTTPException | `detail="Invalid or expired token"` — swallows the underlying error type |
| Any unhandled catch-all | 500 | `INTERNAL_ERROR` |

⚠️ `get_current_user` (security.py) raises a plain `HTTPException(401)` rather than a
domain/application exception, so **401 responses do not use the ErrorEnvelope** — a
documented design deviation (see §7).

---

## 6. Cross-File Consistency

### 6.1 Dependency rules

- `presentation/` → only `application`, `domain`, FastAPI, Pydantic. Verified:
  `rg` shows **no `import app.infrastructure`** anywhere under `src/app/presentation/`.
- The **single documented exception**: `infrastructure/notifications/websocket_notification_service.py`
  imports `presentation.websocket.connection_manager` (allowed per ARCHITECTURE.md —
  connection state is transport-coupled).
- **Two-tier provider wiring** (`core/providers.py` + `bootstrap/container.py`):
  - The 36 **leaf providers** (repositories, ports: `get_<repo>`, `get_token_service`,
    `get_authorization_service`, etc.) are stubs that raise `NotImplementedError`; the
    container overrides each with a real implementation via `app.dependency_overrides`
    (36 overrides in `container.py`, 1:1 with the stubs).
  - The ~80 **use-case providers** (`get_<use_case>_use_case`) are **not stubbed and not
    overridden** — they are self-wiring factories: each takes the leaf providers as
    `Depends(...)` default args and constructs the real `XxxUseCase(...)` on every call
    (e.g. `providers.py:218-235`). Because the leaves are overridden, a use-case provider
    resolves correctly without a dedicated override. ⚠️ Trade-off: no singleton/lazy
    caching of use cases (they are rebuilt per request — cheap, stateless, fine).

### 6.2 Naming & shape consistency

- Endpoint `operation_id`s are unique and match use-case names (`admin_create_user`, etc.).
- Response `schema` names mirror `Result` DTOs (e.g., `ProjectResponse` ↔ `ProjectResult`).
- HTTP verbs and 201-for-CREATE are consistent.
- Compensation paths (e.g., `submit_delivery` → `DeliveryResponse`) are consistent.

### 6.3 Files that are out of date relative to the shipped implementation

- ⚠️ `src/app/presentation/README.md` — claims the package is "intentionally empty"
  and "no real code … is written here"; **factually stale** — the package now contains all
  routers/schemas. Anyone reading the repo will be misled.
- ⚠️ `README.md` (root) — architecture table reads `infrastructure` = "…MySQL/Alembic
  migrations…" but the stack is **Postgres** (docker-compose.yml, INFRASTRUCTURE.md).

---

## 7. Critical Gaps & Inconsistencies

1. **BUG (§ 3.4 / `form/router.py:135`)**: `GET /form-templates/{template_id}` calls
   `GetFormTemplateQuery(category_id=template_id)` — the path var `template_id` is passed
   as a **category_id**; the `GetFormTemplateUseCase` then looks up the *published template
   for a category*. So the endpoint actually returns the template for the **category**
   whose ID was supplied, not a template by its own ID, and a request for a real template
   ID will raise `EntityNotFoundError` (404). Route path, schema, and op_id all say
   "template_id" — this is a latent bug.
2. **Pagination is fictional**: `PageQuery` paginates only the *client-side* length
   (`projects/_pagination_meta` computed from `len(projects)`, no `.offset/.limit` passed
   to any `Query`/repo). `GET /projects`, `/projects/my`, `/reviews/pending`,
   `/reviews/supervisor/projects` — all do DB listing then slice meta. `total_items` equals
   the returned page length, never the DB total. **Partial fix (2026-08-09):** `GET /users`
   (`admin_list_users`, §3.2/17) is the exception — it passes real `limit`/`offset` to
   `IUserRepository.list_all`/`list_by_status` and reports a true `count_all` total. Use it
   as the reference for fixing the remaining affected endpoints; this fix is scoped to this
   one endpoint only.
3. **401 drops the envelope**: `core/security.py` raises raw `HTTPException(401)`, so
   invalid/expired token responses are `{"detail": "..."}` not `ErrorEnvelope`.
4. **WebSocket auth/error handling is unguarded** (`websocket/router.py`): if
   `decode_access_token` raises, there is no try/except — the WS will abruptly close
   (500-style) instead of a clean close/error frame; token in a query string is a
   security smell (logs/leaks).
5. **Modularity leak — duplicated mapping helpers**: `_to_budget_response` /
   `_pagination_meta` are copy-pasted in `project/router.py` and `review/router.py`;
   `_to_application_response` duplicated. Cross-file consistency issue.
6. **`GET /auth/me` reads repos directly** instead of a Query UseCase — inconsistent with
   the "one handler = one UseCase" convention.
7. **`create_project` dual-path** (self vs on-behalf) routes on a body field
   `customer_user_id` — matches Code Domain split (`CreateProjectOnBehalfCommand`), but
   the same endpoint silently picks a different use case based on a body field (DRY vs
   clarity trade-off; intentional per AGENTS.md §Pattern B).
8. **No health/readiness endpoint** for the container/doc stack, and **no OpenAPI
   `responses` / `400`, `401`, `403`, `404`, `409`, `422`, `500` documented** on individual
   routes (global handlers exist but the API docs remain generic).
9. `PageQuery` has an `offset` property (`core/pagination.py:10`) that **nothing uses**.

---

## 8. Summary & Score

| Dimension | Assessment |
|---|---|
| Architecture compliance | **Strong** — layering, dependency direction, DI-override seam, envelope/error mapping all respected. |
| API surface coverage | **Strong** — 81 HTTP endpoints + 1 WebSocket covering all 9 contexts. |
| Consistency (bytes/rules) | **Good but leaky** — 2 stale README claims, 401 global exception, WS unguarded, duplicated mappers. |
| Correctness risk | **1 confirmed latent bug** (form-template path variable misuse at §7.1), fake pagination, WS close. |
| Production readiness | **Not yet** — no auth/refresh storage solution verified here, error envelope deviation on 401s, no WS error handling. |

**Readiness to enter public alpha:** the surface area is real and well-formed (Phase-1
design fidelity), but item #1, #4, and #8 in §7 should be fixed before signaling a stable
HTTP API. Overall active architectural health: **~85/100** for structure, **~70/100** for
runtime robustness as-shipped.