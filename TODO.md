# TODO.md — Phased Checklist

Usage guide: Check each item once it is completed and tested. The suggested order should
be followed because later contexts depend on the Interfaces of previous contexts (for
example, `project` requires `freelancer`, `category`, and `form`).

## Phase 0 — Project Bootstrap

- [x] `pyproject.toml` with dev dependencies (`pytest`, `pytest-cov`, `mypy`, `ruff`)
- [x] Create folder structure `src/app/{domain,application,infrastructure,presentation}` according to
      `ARCHITECTURE.md`
- [x] `app/domain/shared/*` (Entity, ValueObject, base exceptions, events)
- [x] `app/application/shared/*` (Base UseCase, ports, authorization, base exceptions)
- [x] `tests/conftest.py` + `tests/fakes/` (Common Fakes: Clock, IdGenerator, UnitOfWork,
      PasswordHasher, TokenService, AuthorizationService)
- [x] Local CI: Script/Makefile for `pytest`, `mypy`, `ruff`

## Phase 1 — IAM

### Domain

- [x] Value Objects: `Email`, `PasswordHash`, `PhoneNumber`
- [x] Enum: `UserStatus`
- [x] Entities: `User`, `Role`, `Permission`, `UserRole`, `RolePermission`, `RefreshToken`
- [x] IAM-specific Exceptions
- [x] Repository Interfaces: `IUserRepository`, `IRoleRepository`, `IPermissionRepository`,
      `IUserRoleRepository`, `IRolePermissionRepository`, `IRefreshTokenRepository`
- [x] Unit tests for all Entities (happy-path + all exception paths)

### Application

- [x] DTOs (`dto.py`)
- [x] Use Cases: RegisterUser, LoginUser, LogoutUser, RefreshToken, ChangePassword,
      ForgotPassword, BlockUser, ActivateUser, AssignRole, RemoveRole, GrantPermission,
      RevokePermission
- [x] IAM Fake Repositories in `tests/fakes/`
- [x] Use Case tests (happy-path + every Exception)

## Phase 2 — Category

### Domain

- [x] Entities: `Category`, `CategorySupervisor`
- [x] Repository Interfaces + Exceptions
- [x] Unit tests

### Application

- [x] Use Cases: CreateCategory, UpdateCategory, DeleteCategory, AssignSupervisor,
      RemoveSupervisor, GetCategories
- [x] GetCategoryProjects (deferred — requires `IProjectRepository`, completed after Phase 5)
- [x] Use Case tests

## Phase 3 — Freelancer Management

### Domain

- [x] Enums: `FreelancerApprovalStatus`, `FreelancerLevelAccessType`
- [x] Entities: `FreelancerLevel`, `FreelancerProfile`, `FreelancerLevelHistory`,
      `Resume`, `PortfolioItem`
- [x] Repository Interfaces + Exceptions
- [x] Unit tests

### Application

- [x] Use Cases: CreateFreelancerProfile, UpdateFreelancerProfile, UploadResume,
      UpdateResume, AddPortfolioItem, UpdatePortfolioItem, DeletePortfolioItem,
      SubmitFreelancerApproval, ApproveFreelancer, RejectFreelancer,
      AssignFreelancerLevel, GetFreelancerProfile
- [ ] GetFreelancerStatistics (deferred — requires `IRatingRepository` and
      `IProjectRepository`/`IProjectApplicationRepository`, completed after Phase 7)
- [x] Use Case tests

## Phase 4 — Dynamic Form Engine

### Domain

- [x] Enums: `FormFieldType`, `FormTemplateStatus`
- [x] Entities: `FormTemplate`, `FormField`, `FormFieldOption`
- [x] Repository Interface + Exceptions
- [x] Unit tests

### Application

- [x] Use Cases: CreateFormTemplate, UpdateFormTemplate, PublishFormTemplate, AddField,
      UpdateField, RemoveField, AddFieldOption, GetFormTemplate
- [x] Use Case tests

## Phase 5 — Project Management (Core Domain)

### Domain

- [x] Enums (Status, Visibility, Priority, BudgetType, ApplicationStatus,
      DeliveryStatus, RevisionRequestStatus)
- [x] Value Objects: `Budget`, `ProjectCode`
- [x] Entities: `Project`, `ProjectApplication`, `ProjectDelivery`,
      `ProjectRevisionRequest`, `ProjectStatusHistory`
- [x] Domain Services: `RevisionPolicy`, `FreelancerEligibilityPolicy`
- [x] Repository Interfaces + Exceptions
- [x] Complete unit tests for project state machine (all valid/invalid transitions)

### Application

- [x] Core Flow Use Cases: CreateProject, PublishProject, CancelProject,
      ApplyForProject, WithdrawApplication, ViewApplications, AcceptFreelancer,
      RejectFreelancer, StartProject, SubmitDelivery, RequestRevision, CompleteProject,
      GetProjectDetails, GetMyProjects, GetAvailableProjects
- [x] Use Case tests (including End-to-End scenario with Fakes: Create → Publish → Apply →
      Accept → Start → SubmitDelivery → RequestRevision → SubmitDelivery → Complete)
- [x] `GetCategoryProjects` (deferred from Phase 2) implemented once `IProjectRepository` existed

## Phase 6 — Quality Assurance / Supervisor Review

### Domain

- [x] Enum: `ReviewStatus`
- [x] Entity: `SupervisorReview`
- [x] Repository Interface + Exceptions
- [x] Unit tests

### Application

- [x] Use Cases: GetSupervisorProjects, GetPendingReviews, ReviewDelivery,
      ApproveDelivery, RejectDelivery
- [x] Use Case tests (including validation constraint: "only the supervisor of the same category")

Note: `ISupervisorReviewRepository` gained an `update` method (deviation — a pre-existing
PENDING review must be persisted after being decided). `SubmitDeliveryUseCase` pre-creates the
PENDING `SupervisorReview` when a delivery is routed to supervisor review.

## Phase 7 — Feedback & Rating

### Domain

- [x] Entities: `CustomerReview`, `Rating`
- [x] Repository Interfaces + Exceptions
- [x] Unit tests (including score range validation from 1 to 5)

### Application

- [x] Use Cases: SubmitReview, SubmitRating, GetFreelancerRatings, GetProjectRating
- [x] Tests (including validation: "only after Completion")

Note: `SubmitReviewUseCase` decides the project directly (APPROVED -> COMPLETED via
`Project.complete`, REJECTED -> opens a `ProjectRevisionRequest` and moves to
REVISION_REQUESTED). `SubmitRatingUseCase` requires the project to be COMPLETED and a
`CustomerReview` to exist (rating references the review).

## Phase 8 — Communication / Ticketing

### Domain

- [x] Enums: `TicketStatus`, `TicketPriority`, `TicketMessageType`,
      `TicketParticipantRole`
- [x] Entities: `Ticket`, `TicketParticipant`, `TicketMessage`
- [x] Repository Interfaces + Exceptions
- [x] Unit tests

### Application

- [x] Use Cases: CreateTicket, AssignTicket, SendMessage, GetTicketMessages,
      CloseTicket, GetUserTickets
- [x] Tests

Note: added `ITicketCodeGenerator` port (shared) for `TCK-<year>-<seq>` codes. SendMessage
and CloseTicket require the actor to be a ticket participant; assignees are added as
participants on assignment.

## Phase 9 — Reporting & Analytics (Read-Only)

### Domain

- [ ] Read Models: `DashboardStatistics`, `ProjectStatistics`, `UserStatistics`,
      `FreelancerStatistics`, `CustomerStatistics`
- [ ] Repository Interface: `IReportingReadRepository`

### Application

- [ ] Use Cases: GetDashboardStatistics, GetUserStatistics, GetProjectStatistics,
      GetFreelancerStatistics, GetCustomerStatistics, GetSystemAnalytics
- [ ] Tests with Fake Read Repository

## Phase 10 — Phase One Finalization

- [ ] Complete Coverage Review (>=90% on domain and application)
- [ ] Review `mypy --strict`
- [ ] Review that there are no forbidden imports in domain/application
      (`grep -R "^import fastapi\|^import sqlalchemy\|^import pydantic" src/app/domain src/app/application`)
- [ ] Final documentation: Update `ARCHITECTURE.md`/`DOMAIN.md`/`APPLICATION.md` with any
      actual deviations from the initial plan
- [ ] Prepare the exact list of Interfaces that Phase 2 (`infrastructure`/`presentation`) must
      implement (automatic output: all `I*` classes in `domain`/`application`)

## Phase 2 (Later — Out of Current Scope)

- [ ] `infrastructure`: SQLAlchemy models + repository implementations
- [ ] `infrastructure/security`: JWT (`PyJWT`) + password hashing (`argon2-cffi`)
- [ ] `infrastructure/storage`: file asset storage (local/S3)
- [ ] `presentation`: FastAPI routers + Pydantic schemas + dependency wiring +
      Global Exception Handler (according to the mapping table in `ERROR_HANDLING.md`)
- [ ] Integration tests (with real DB or testcontainers)
