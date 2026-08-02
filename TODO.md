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
- [ ] GetCategoryProjects (deferred — requires `IProjectRepository`, completed after Phase 5)
- [x] Use Case tests

## Phase 3 — Freelancer Management

### Domain

- [ ] Enums: `FreelancerApprovalStatus`, `FreelancerLevelAccessType`
- [ ] Entities: `FreelancerLevel`, `FreelancerProfile`, `FreelancerLevelHistory`,
      `Resume`, `PortfolioItem`
- [ ] Repository Interfaces + Exceptions
- [ ] Unit tests

### Application

- [ ] Use Cases: CreateFreelancerProfile, UpdateFreelancerProfile, UploadResume,
      UpdateResume, AddPortfolioItem, UpdatePortfolioItem, DeletePortfolioItem,
      SubmitFreelancerApproval, ApproveFreelancer, RejectFreelancer,
      AssignFreelancerLevel, GetFreelancerProfile, GetFreelancerStatistics
- [ ] Use Case tests

## Phase 4 — Dynamic Form Engine

### Domain

- [ ] Enums: `FormFieldType`, `FormTemplateStatus`
- [ ] Entities: `FormTemplate`, `FormField`, `FormFieldOption`
- [ ] Repository Interface + Exceptions
- [ ] Unit tests

### Application

- [ ] Use Cases: CreateFormTemplate, UpdateFormTemplate, PublishFormTemplate, AddField,
      UpdateField, RemoveField, AddFieldOption, GetFormTemplate
- [ ] Use Case tests

## Phase 5 — Project Management (Core Domain)

### Domain

- [ ] Enums (Status, Visibility, Priority, BudgetType, ApplicationStatus,
      DeliveryStatus, RevisionRequestStatus)
- [ ] Value Objects: `Budget`, `ProjectCode`
- [ ] Entities: `Project`, `ProjectApplication`, `ProjectDelivery`,
      `ProjectRevisionRequest`, `ProjectStatusHistory`
- [ ] Domain Services: `RevisionPolicy`, `FreelancerEligibilityPolicy`
- [ ] Repository Interfaces + Exceptions
- [ ] Complete unit tests for project state machine (all valid/invalid transitions)

### Application

- [ ] Core Flow Use Cases: CreateProject, PublishProject, CancelProject,
      ApplyForProject, WithdrawApplication, ViewApplications, AcceptFreelancer,
      RejectFreelancer, StartProject, SubmitDelivery, RequestRevision, CompleteProject,
      GetProjectDetails, GetMyProjects, GetAvailableProjects
- [ ] Use Case tests (including End-to-End scenario with Fakes: Create → Publish → Apply →
      Accept → Start → SubmitDelivery → RequestRevision → SubmitDelivery → Complete)

## Phase 6 — Quality Assurance / Supervisor Review

### Domain

- [ ] Enum: `ReviewStatus`
- [ ] Entity: `SupervisorReview`
- [ ] Repository Interface + Exceptions
- [ ] Unit tests

### Application

- [ ] Use Cases: GetSupervisorProjects, GetPendingReviews, ReviewDelivery,
      ApproveDelivery, RejectDelivery
- [ ] Use Case tests (including validation constraint: "only the supervisor of the same category")

## Phase 7 — Feedback & Rating

### Domain

- [ ] Entities: `CustomerReview`, `Rating`
- [ ] Repository Interfaces + Exceptions
- [ ] Unit tests (including score range validation from 1 to 5)

### Application

- [ ] Use Cases: SubmitReview, SubmitRating, GetFreelancerRatings, GetProjectRating
- [ ] Tests (including validation: "only after Completion")

## Phase 8 — Communication / Ticketing

### Domain

- [ ] Enums: `TicketStatus`, `TicketPriority`, `TicketMessageType`,
      `TicketParticipantRole`
- [ ] Entities: `Ticket`, `TicketParticipant`, `TicketMessage`
- [ ] Repository Interfaces + Exceptions
- [ ] Unit tests

### Application

- [ ] Use Cases: CreateTicket, AssignTicket, SendMessage, GetTicketMessages,
      CloseTicket, GetUserTickets
- [ ] Tests

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
