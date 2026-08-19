# ARCHITECTURE.md — Clean Architecture (Python)

## 1. Layers and Responsibilities

```
┌─────────────────────────────────────────────────────────┐
│  bootstrap        — Composition Root ("Main Component"):  │
│                      the ONLY package allowed to import    │
│                      both presentation and infrastructure  │
├─────────────────────────────────────────────────────────┤
│  presentation      — FastAPI routers, Pydantic schemas,    │
│                      provider *stubs* for DI, WebSocket     │
├─────────────────────────────────────────────────────────┤
│  application       — Use Cases, DTOs,                      │
│                      Service Interfaces (Ports), Application │
│                      Exceptions, Orchestration (async)      │
├─────────────────────────────────────────────────────────┤
│  domain            — Entities, Value Objects,               │
│                      Enums, Domain Exceptions,               │
│                      Repository Interfaces, Domain Services  │
├─────────────────────────────────────────────────────────┤
│  infrastructure    — SQLAlchemy repos, JWT impl,             │
│                      password hasher impl, WebSocket notifier │
└─────────────────────────────────────────────────────────┘
```

**Dependency Rule:** dependencies are only allowed inward. `domain` is independent of
everything. `application` only knows `domain`. `infrastructure` and `presentation` both know
`application`/`domain`, but the reverse is forbidden. **In addition, `presentation` never
imports `infrastructure`, and vice versa** — these two packages are fully independent of
each other. The only package allowed to import both is `bootstrap/`, which corresponds to
the **"Main Component"** concept from the Clean Architecture book: a component outside all
four rings whose sole responsibility is wiring concrete implementations to abstractions. See
`PRESENTATION.md` §3 for the exact mechanism (provider stubs +
`app.dependency_overrides`).

## 2. Folder Structure

```
project_root/
├── pyproject.toml
├── AGENTS.md
├── ARCHITECTURE.md
├── DOMAIN.md
├── APPLICATION.md
├── AUTHORIZATION.md
├── ERROR_HANDLING.md
├── API_DESIGN.md
├── PRESENTATION.md
├── INFRASTRUCTURE.md
├── DOCKER.md
├── TESTING.md
├── TODO.md
├── Dockerfile
├── docker-compose.yml
├── .env.example
├── src/
│   └── app/
│       ├── __init__.py
│       ├── domain/                        # unchanged from Phase 1 — see DOMAIN.md
│       │   ├── shared/
│       │   ├── iam/
│       │   ├── freelancer/
│       │   ├── category/
│       │   ├── form/
│       │   ├── project/
│       │   ├── review/
│       │   ├── feedback/
│       │   ├── ticketing/
│       │   └── reporting/
│       │
│       ├── application/                   # unchanged structure from Phase 1, now async
│       │   ├── shared/                     # use_case.py, ports.py, authorization.py, exceptions.py
│       │   ├── iam/, freelancer/, category/, form/, project/, review/, feedback/,
│       │   │   ticketing/, reporting/       # each: use_cases/, dto.py, exceptions.py,
│       │   │                                #   permissions.py (PERMISSION_* constants)
│       │
│       ├── infrastructure/                 # Phase 2 — real implementation, see INFRASTRUCTURE.md
│       │   ├── config.py
│       │   ├── db/                          # base.py, session.py, unit_of_work.py, models/
│       │   ├── repositories/                # one file per Repository Interface
│       │   ├── security/                    # password_hasher.py, token_service.py,
│       │   │                                #   authorization_service.py
│       │   ├── notifications/                # websocket_notification_service.py
│       │   ├── clock.py, id_generator.py, code_generators.py
│       │   ├── migrations/                   # Alembic
│       │   └── seed/                         # seed_data.py, run_seed.py
│       │
│       ├── presentation/                    # Phase 2 — real implementation, see PRESENTATION.md
│       │   ├── main.py                       # create_app() — no infrastructure imports
│       │   ├── core/                         # envelope.py, error_handlers.py, security.py,
│       │   │                                #   providers.py (stubs only), pagination.py
│       │   ├── websocket/                    # connection_manager.py, router.py
│       │   └── api/v1/                       # one subpackage per bounded context + auth/
│       │
│       └── bootstrap/                       # Phase 2 — Composition Root, see PRESENTATION.md §3
│           ├── container.py                  # overrides every provider stub with real infra
│           └── run.py                        # uvicorn entrypoint: `app.bootstrap.run:app`
│
└── tests/
    ├── domain/, application/                # Phase 1 — Fake-based, no external services
    ├── infrastructure/                       # Phase 2 — against a real Postgres
    └── presentation/                         # Phase 2 — httpx/TestClient + dependency_overrides
```

Note: we use `src/` layout to prevent incorrect imports from the repository root and keep
packaging clean (`pip install -e .`).

## 3. Key Design Patterns Used

- **Repository Pattern**: each Aggregate has a Repository Interface in `domain` (such as
  `IProjectRepository`); methods are named based on the domain's Ubiquitous Language (not raw
  CRUD) — for example `find_by_code`, `list_available_for_freelancer`. As of Phase 2, every
  method on these interfaces is `async def` and every caller `await`s it (see §7).
- **Unit of Work**: multi-Aggregate transactions (such as `AcceptFreelancer`, which changes
  both `Project` and `ProjectApplication`) are controlled through `IUnitOfWork`, implemented
  in Phase 2 by `SqlAlchemyUnitOfWork` as an async context manager (`__aenter__`/`__aexit__`).
- **Command Pattern for Use Cases**: each Use Case = one class with
  `async def execute(command) -> result`.
- **Ports & Adapters (Hexagonal)**: every external service (Token, Hash, Email/Notification,
  Clock, IdGenerator, Authorization) is defined as an Interface (`Port`) in the
  application/domain layer; the real implementation lives in `infrastructure` (Phase 2) and
  is wired in via `bootstrap/` (never imported directly by `presentation`).
- **Composition Root ("Main")**: `bootstrap/container.py` is the single place in the whole
  codebase allowed to know about both `presentation` and `infrastructure` concrete classes.
  `presentation` only ever references abstract provider stubs; `bootstrap` overrides them via
  FastAPI's `app.dependency_overrides`.
- **Domain Events (defined, not yet wired)**: `IEventPublisher` exists in `domain/shared` for
  future loose coupling between contexts, but no Phase 1/2 flow uses it yet — every current
  cross-context effect (e.g. `SubmitReview` completing a project) is done directly inside the
  same use case/unit of work.
- **Specification Pattern (optional, for complex Reporting/Project queries)**: can be used at
  the Repository Interface level without exposing ORM details; not required for the
  current Reporting scope (unparameterized aggregate queries).

## 4. Bounded Context ⇄ Layer Mapping (Summary)

| Context    | Domain Entities                                                                            | Key Repository                                                                   | Key Use Cases                                                                                      |
| ---------- | ------------------------------------------------------------------------------------------ | -------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------- |
| IAM        | User, Role, Permission, UserRole, RolePermission, RefreshToken                             | IUserRepository, IRoleRepository, IPermissionRepository, IRefreshTokenRepository | RegisterUser, LoginUser, RefreshToken, AssignRole, Admin User CRUD                                 |
| Freelancer | FreelancerProfile, FreelancerLevel, Resume, PortfolioItem                                  | IFreelancerProfileRepository, IFreelancerLevelRepository                         | CreateFreelancerProfile, SubmitFreelancerApproval, ApproveFreelancer                               |
| Category   | Category, CategorySupervisor                                                               | ICategoryRepository                                                              | CreateCategory, AssignSupervisor                                                                   |
| Form       | FormTemplate, FormField, FormFieldOption                                                   | IFormTemplateRepository                                                          | CreateFormTemplate, PublishFormTemplate                                                            |
| Project    | Project, ProjectApplication, ProjectDelivery, ProjectRevisionRequest, ProjectStatusHistory | IProjectRepository, IProjectApplicationRepository, IProjectDeliveryRepository    | CreateProject, ApplyForProject, AcceptFreelancer, SubmitDelivery, RequestRevision, CompleteProject |
| Review     | SupervisorReview                                                                           | ISupervisorReviewRepository                                                      | ReviewDelivery, ApproveDelivery, RejectDelivery                                                    |
| Feedback   | CustomerReview, Rating                                                                     | IRatingRepository, ICustomerReviewRepository                                     | SubmitReview, SubmitRating                                                                         |
| Ticketing  | Ticket, TicketParticipant, TicketMessage                                                   | ITicketRepository                                                                | CreateTicket, SendMessage, CloseTicket                                                             |
| Reporting  | (Read Models)                                                                              | IReportingReadRepository                                                         | GetDashboardStatistics                                                                             |

## 5. Phase Two — Now Starting

See `PRESENTATION.md`, `INFRASTRUCTURE.md`, `DOCKER.md` for full detail. Summary:

- **Prerequisite**: the `application` layer (and every `domain` repository/port interface it
  depends on) is converted to `async def` before any real infrastructure/presentation code is
  written — required for FastAPI + async SQLAlchemy.
- `infrastructure`: SQLAlchemy + PostgreSQL repositories implementing every `domain`
  Repository Interface; `infrastructure/security` for JWT (`PyJWT`) and password hashing
  (`argon2-cffi`); `infrastructure/notifications` for WebSocket-based real-time notification;
  Alembic migrations; an idempotent seed script for roles/permissions/admin bootstrap.
- `presentation`: FastAPI routers per bounded context, a standard response envelope
  (`API_DESIGN.md`), a global exception handler mapping the `ERROR_HANDLING.md` hierarchy to
  HTTP status codes, and provider _stubs_ only — no direct infrastructure imports.
- `bootstrap`: the Composition Root wiring `presentation` provider stubs to real
  `infrastructure` implementations; the actual uvicorn entrypoint is
  `app.bootstrap.run:app`, not `app.presentation.main:app`.

### 5.1 Complete list of interfaces Phase 2 must implement (all `I*` classes)

`domain` repositories/services:
`ICategoryRepository`, `ICategorySupervisorRepository`, `IUserRepository`,
`IUserRoleRepository`, `IRoleRepository`, `IRolePermissionRepository`,
`IPermissionRepository`, `IRefreshTokenRepository`, `IFreelancerProfileRepository`,
`IFreelancerLevelRepository`, `IFreelancerLevelHistoryRepository`, `IResumeRepository`,
`IPortfolioItemRepository`, `IFormTemplateRepository`, `IProjectRepository`,
`IProjectApplicationRepository`, `IProjectDeliveryRepository`,
`IProjectRevisionRequestRepository`, `IProjectStatusHistoryRepository`,
`ISupervisorReviewRepository`, `ICustomerReviewRepository`, `IRatingRepository`,
`ITicketRepository`, `ITicketMessageRepository`, `ITicketParticipantRepository`,
`IReportingReadRepository`.

`application` shared services (implemented in `infrastructure/security`,
`infrastructure/notifications`, ...): `IPasswordHasher`, `ITokenService`, `IIdGenerator`,
`IClock`, `IProjectCodeGenerator`, `ITicketCodeGenerator`, `IUnitOfWork`, `IEventPublisher`,
`INotificationService`, `IRealtimeNotifier` (new — see `INFRASTRUCTURE.md` §6),
`IFileStorageService`, `IAuthorizationService`.

> Before implementing each interface, cross-check `DOMAIN.md`/`AUTHORIZATION.md` for any
> repository method additions made during the authorization-hardening pass (e.g. a
> last-active-admin lookup on `IUserRoleRepository`) — this list reflects the interfaces as
> of the start of Phase 2 and must be re-verified against the actual current interface
> definitions before starting implementation, not assumed complete.

## 6. Deviations from the Initial Plan (Recorded)

- **No event bus in Phase 1/2 flows**: cross-context effects are performed directly inside
  the same use case/unit of work; `IEventPublisher` exists but is unwired.
- **`IFreelancerLevelHistoryRepository`**, **`ISupervisorReviewRepository.update`**, and
  **`ITicketCodeGenerator`** were added during Phase 1 hardening, beyond the original
  `DOMAIN.md` interface list.
- **Authorization hardening (recorded during the Phase 1 hardening pass)**: owned-resource
  use cases now use the two-tier `_own`/`_any` convention via `authorize_owned_action`
  (`AUTHORIZATION.md`); creation-of-entity-for-another-user use cases follow the Self vs.
  On-Behalf Pattern B split (thin self-service + thin on-behalf use case sharing a private
  helper); admin IAM CRUD use cases (`AdminCreateUser`, `AdminUpdateUser`, `AdminDeleteUser`)
  were added. Role/Permission **catalog entities** are seed-only and immutable
  (`SystemRoleImmutableError` is reserved for that, currently unraised), while
  `UserRole`/`RolePermission` **links** stay fully mutable — the only restriction is
  `RemoveRoleUseCase`'s last-admin rule (`LastAdminRoleRemovalError`, HTTP 409). These two
  concerns must not be conflated (`AUTHORIZATION.md` §4).
- **Reporting read models**: statistics read models use `Decimal` for `total_revenue` and
  `average_rating`; a composite `SystemAnalytics` read model was added for
  `GetSystemAnalyticsUseCase` (not in the original `DOMAIN.md`).
- **Enum values** use `UPPER_SNAKE` (e.g. `ProjectStatus.COMPLETED`, `UserStatus.ACTIVE`) per
  the DBML-aligned convention.
- **Phase 2 additions (this document)**: introduced the `bootstrap/` package as the
  Composition Root so that `presentation` never imports `infrastructure` directly, correcting
  an earlier draft that placed DI wiring inside `presentation/core/container.py`.
