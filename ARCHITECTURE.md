```md
# ARCHITECTURE.md — Clean Architecture (Python)

## 1. Layers and Responsibilities
```

┌─────────────────────────────────────────────────────────┐
│ presentation (Phase 2) — FastAPI routers, schemas, │
│ dependency wiring, controllers │
├─────────────────────────────────────────────────────────┤
│ application (Phase 1) — Use Cases, DTOs, │
│ Service Interfaces (Ports), Application │
│ Exceptions, Orchestration │
├─────────────────────────────────────────────────────────┤
│ domain (Phase 1) — Entities, Value Objects, │
│ Enums, Domain Exceptions, │
│ Repository Interfaces, Domain Services │
├─────────────────────────────────────────────────────────┤
│ infrastructure (Phase 2) — SQLAlchemy repos, JWT impl, │
│ password hasher impl, email/file storage │
└─────────────────────────────────────────────────────────┘

```

Dependency Rule: Dependencies are only allowed inward (towards domain).
`domain` is independent of everything. `application` only knows `domain`.
`infrastructure` and `presentation` both know `application`/`domain`, but the reverse
is forbidden.

## 2. Folder Structure (Phase 1)

```

project_root/
├── pyproject.toml
├── AGENTS.md
├── ARCHITECTURE.md
├── DOMAIN.md
├── APPLICATION.md
├── ERROR_HANDLING.md
├── TESTING.md
├── TODO.md
├── src/
│ └── app/
│ ├── **init**.py
│ ├── domain/
│ │ ├── **init**.py
│ │ ├── shared/ # Shared code between all contexts
│ │ │ ├── **init**.py
│ │ │ ├── entity.py # base Entity/AggregateRoot
│ │ │ ├── value_object.py # base ValueObject
│ │ │ ├── exceptions.py # DomainError, NotFoundError, ...
│ │ │ ├── events.py # DomainEvent base + IEventPublisher
│ │ │ └── types.py # EntityId, Money, DateRange, ...
│ │ │
│ │ ├── iam/
│ │ │ ├── **init**.py
│ │ │ ├── entities.py # User, Role, Permission, RefreshToken
│ │ │ ├── value_objects.py # Email, PasswordHash, PhoneNumber
│ │ │ ├── enums.py # UserStatus
│ │ │ ├── exceptions.py
│ │ │ └── repositories.py # IUserRepository, IRoleRepository, ...
│ │ │
│ │ ├── freelancer/
│ │ │ ├── entities.py # FreelancerProfile, Resume, PortfolioItem, FreelancerLevel
│ │ │ ├── value_objects.py
│ │ │ ├── enums.py # FreelancerApprovalStatus
│ │ │ ├── exceptions.py
│ │ │ └── repositories.py
│ │ │
│ │ ├── category/
│ │ │ ├── entities.py # Category, CategorySupervisor
│ │ │ ├── exceptions.py
│ │ │ └── repositories.py
│ │ │
│ │ ├── form/
│ │ │ ├── entities.py # FormTemplate, FormField, FormFieldOption
│ │ │ ├── enums.py # FormFieldType
│ │ │ ├── exceptions.py
│ │ │ └── repositories.py
│ │ │
│ │ ├── project/
│ │ │ ├── entities.py # Project, ProjectApplication, ProjectDelivery, ...
│ │ │ ├── value_objects.py # Budget, ProjectCode
│ │ │ ├── enums.py # ProjectStatus, ApplicationStatus, DeliveryStatus, ...
│ │ │ ├── exceptions.py
│ │ │ ├── services.py # domain service: RevisionPolicy, AssignmentPolicy
│ │ │ └── repositories.py
│ │ │
│ │ ├── review/
│ │ │ ├── entities.py # SupervisorReview
│ │ │ ├── enums.py # ReviewStatus
│ │ │ ├── exceptions.py
│ │ │ └── repositories.py
│ │ │
│ │ ├── feedback/
│ │ │ ├── entities.py # CustomerReview, Rating
│ │ │ ├── exceptions.py
│ │ │ └── repositories.py
│ │ │
│ │ ├── ticketing/
│ │ │ ├── entities.py # Ticket, TicketParticipant, TicketMessage, Attachment
│ │ │ ├── enums.py
│ │ │ ├── exceptions.py
│ │ │ └── repositories.py
│ │ │
│ │ └── reporting/
│ │ ├── read_models.py # DTO-like read models (Dashboard/Statistics)
│ │ └── repositories.py # IReportingReadRepository (read-only)
│ │
│ ├── application/
│ │ ├── **init**.py
│ │ ├── shared/
│ │ │ ├── **init**.py
│ │ │ ├── use_case.py # base UseCase[TRequest, TResponse]
│ │ │ ├── exceptions.py # ApplicationError hierarchy
│ │ │ ├── ports.py # ITokenService, IPasswordHasher, IClock, IIdGenerator,
│ │ │ │ # IUnitOfWork, IEventPublisher, INotificationService,
│ │ │ │ # IFileStorageService
│ │ │ └── authorization.py # IAuthorizationService (RBAC check port)
│ │ │
│ │ ├── iam/
│ │ │ ├── use_cases/
│ │ │ │ ├── register_user.py
│ │ │ │ ├── login_user.py
│ │ │ │ ├── logout_user.py
│ │ │ │ ├── refresh_token.py
│ │ │ │ ├── change_password.py
│ │ │ │ ├── forgot_password.py
│ │ │ │ ├── block_user.py
│ │ │ │ ├── activate_user.py
│ │ │ │ ├── assign_role.py
│ │ │ │ ├── remove_role.py
│ │ │ │ ├── grant_permission.py
│ │ │ │ └── revoke_permission.py
│ │ │ ├── dto.py
│ │ │ └── exceptions.py
│ │ │
│ │ ├── freelancer/ (same pattern: use_cases/, dto.py, exceptions.py)
│ │ ├── category/
│ │ ├── form/
│ │ ├── project/
│ │ ├── review/
│ │ ├── feedback/
│ │ ├── ticketing/
│ │ └── reporting/
│ │
│ ├── infrastructure/ # Phase 2 — currently only skeleton + README
│ │ └── README.md
│ │
│ └── presentation/ # Phase 2 — currently only skeleton + README
│ └── README.md
│
└── tests/
├── domain/
│ ├── iam/, freelancer/, category/, form/, project/, review/, feedback/, ticketing/
└── application/
├── iam/, freelancer/, category/, form/, project/, review/, feedback/, ticketing/

```

Note: We use `src/` layout to prevent incorrect imports from the repository root and keep
packaging clean (`pip install -e .`).

## 3. Key Design Patterns Used

- **Repository Pattern**: Each Aggregate has a Repository Interface in `domain`
  (such as `IProjectRepository`); methods are named based on the domain's Ubiquitous
  Language (not raw CRUD) — for example `find_by_code`, `list_available_for_freelancer`.
- **Unit of Work**: Multi-Aggregate transactions (such as `AcceptFreelancer` which
  changes both `Project` and `ProjectApplication`) are controlled through `IUnitOfWork`
  defined in `application/shared/ports.py`.
- **Command Pattern for Use Cases**: Each Use Case = one class with `execute(command) -> result`.
- **Ports & Adapters (Hexagonal)**: Every external service (Token, Hash, Email, Storage,
  Clock, IdGenerator) is defined as an Interface (`Port`) in the application/domain
  layer and the real implementation is injected in `infrastructure` (Phase 2).
- **Domain Events (Optional but Recommended)**: For loose coupling between contexts
  (for example `ProjectCompletedEvent` which Feedback context listens to) —
  its Interface (`IEventPublisher`) is defined in `domain/shared/events.py`.
- **Specification Pattern (Optional, for Complex Queries)**: In Reporting/Project
  for complex filters (such as the SQL query example in the third file), the
  Specification pattern can be used at the Repository Interface level without exposing
  ORM details.

## 4. Bounded Context ⇄ Layer Mapping (Summary)

| Context | Domain Entities | Key Repository | Key Use Cases |
|---|---|---|---|
| IAM | User, Role, Permission, UserRole, RolePermission, RefreshToken | IUserRepository, IRoleRepository, IPermissionRepository, IRefreshTokenRepository | RegisterUser, LoginUser, RefreshToken, AssignRole |
| Freelancer | FreelancerProfile, FreelancerLevel, Resume, PortfolioItem | IFreelancerProfileRepository, IFreelancerLevelRepository | CreateFreelancerProfile, SubmitFreelancerApproval, ApproveFreelancer |
| Category | Category, CategorySupervisor | ICategoryRepository | CreateCategory, AssignSupervisor |
| Form | FormTemplate, FormField, FormFieldOption | IFormTemplateRepository | CreateFormTemplate, PublishFormTemplate |
| Project | Project, ProjectApplication, ProjectDelivery, ProjectRevisionRequest, ProjectStatusHistory | IProjectRepository, IProjectApplicationRepository, IProjectDeliveryRepository | CreateProject, ApplyForProject, AcceptFreelancer, SubmitDelivery, RequestRevision, CompleteProject |
| Review | SupervisorReview | ISupervisorReviewRepository | ReviewDelivery, ApproveDelivery, RejectDelivery |
| Feedback | CustomerReview, Rating | IRatingRepository, ICustomerReviewRepository | SubmitReview, SubmitRating |
| Ticketing | Ticket, TicketParticipant, TicketMessage | ITicketRepository | CreateTicket, SendMessage, CloseTicket |
| Reporting | (Read Models) | IReportingReadRepository | GetDashboardStatistics |

## 5. Phase Two (For Awareness Only — Not Implemented Now)

- `infrastructure`: SQLAlchemy + PostgreSQL repositories that implement `domain`
  Interfaces; `infrastructure/security` for JWT (`PyJWT`) and password hash
  (`argon2` or `bcrypt`); `infrastructure/storage` for S3/local file assets.
- `presentation`: FastAPI (routers per context), Pydantic schemas for request/response
  (mapping to application DTOs, not replacing them), dependency injection wiring
  (for example with `punq`/`dependency-injector` or FastAPI `Depends`), middleware for
  global auth/error handling.
```
