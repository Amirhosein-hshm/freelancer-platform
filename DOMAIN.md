# DOMAIN.md — Domain Layer Specification

> **Phase 2 note:** as of Phase 2, every method on every Repository Interface listed below
> (`I*Repository`) becomes `async def`, and every caller in `application`/`infrastructure`
> `await`s it — required for FastAPI + async SQLAlchemy. This document keeps the sync `def`
> notation below for readability, since the signatures themselves (parameters, return types,
> raised exceptions) are otherwise unchanged; treat every `def foo(...)` on a Repository
> Interface as `async def foo(...)`. Entities, Value Objects, and their own methods (e.g.
> `Project.assign_freelancer(...)`) stay synchronous — they are pure in-memory state
> transitions with no I/O, and remain `def`, not `async def`.

This file is the exact reference for implementing `app/domain/*`. Each section includes:
Entity/Value Object, business rules inside the Entity, dedicated Exceptions, and Repository
Interface.

## 0. Shared Kernel (`domain/shared`)

```python
# domain/shared/types.py
EntityId = str  # UUID4 as a string; generated via IIdGenerator in application
                  # (domain never generates UUIDs itself, to stay free of side effects
                  #  unless injected)

# domain/shared/entity.py
class Entity(ABC):
    id: EntityId
    created_at: datetime
    updated_at: datetime | None
    # eq/hash based on id

class AggregateRoot(Entity):
    _domain_events: list[DomainEvent]
    def pull_domain_events(self) -> list[DomainEvent]: ...
    def _record_event(self, event: DomainEvent) -> None: ...

# domain/shared/value_object.py
@dataclass(frozen=True)
class ValueObject(ABC): ...   # eq based on all fields

# domain/shared/exceptions.py
class DomainError(Exception): ...
class EntityNotFoundError(DomainError): ...
class InvalidStateTransitionError(DomainError): ...
class BusinessRuleViolationError(DomainError): ...
class UniqueConstraintViolationError(DomainError): ...

# domain/shared/events.py
@dataclass(frozen=True)
class DomainEvent(ABC):
    occurred_at: datetime

class IEventPublisher(ABC):
    @abstractmethod
    def publish(self, events: list[DomainEvent]) -> None: ...
```

Full Exception hierarchy detail is in `ERROR_HANDLING.md` — every context-specific
Exception must inherit from one of the classes above, never directly from `Exception`.

---

## 1. IAM (`domain/iam`)

### Value Objects

- `Email(value: str)` — validated with a simple regex in `__post_init__`; otherwise
  `InvalidEmailError` (inherits `BusinessRuleViolationError`).
- `PasswordHash(value: str)` — just a wrapper; real hashing happens in `application` via
  `IPasswordHasher`; the Entity never sees plaintext passwords.
- `PhoneNumber(value: str)` — simple format validation.

### Enums

- `UserStatus`: `PENDING, ACTIVE, BLOCKED, ARCHIVED`

### Entities

```python
@dataclass
class User(AggregateRoot):
    email: Email
    phone: PhoneNumber | None
    password_hash: PasswordHash
    first_name: str
    last_name: str
    status: UserStatus
    email_verified_at: datetime | None
    phone_verified_at: datetime | None
    last_login_at: datetime | None
    password_changed_at: datetime | None
    deleted_at: datetime | None

    def activate(self) -> None: ...          # PENDING/BLOCKED -> ACTIVE
    def block(self, reason: str) -> None: ... # ACTIVE -> BLOCKED, raises if ARCHIVED
    def record_login(self, at: datetime) -> None: ...
    def change_password(self, new_hash: PasswordHash, at: datetime) -> None: ...
    def soft_delete(self, at: datetime) -> None: ...
    def is_active(self) -> bool: ...
```

Rule: `block()` on an `ARCHIVED` user must raise `InvalidStateTransitionError`.

```python
@dataclass
class Role(Entity):
    role_key: str
    name: str
    description: str | None
    is_system: bool
    def rename(self, name: str) -> None: ...
    # rule: a role with is_system=True cannot be deleted -> checked in Use Case
    # but role_key can never be changed (immutable business key)

@dataclass
class Permission(Entity):
    permission_key: str
    module: str
    action: str
    description: str | None
    is_system: bool

@dataclass
class UserRole(Entity):
    user_id: EntityId
    role_id: EntityId
    assigned_by_user_id: EntityId
    assigned_at: datetime
    revoked_at: datetime | None
    is_active: bool
    def revoke(self, at: datetime) -> None: ...

@dataclass
class RolePermission(Entity):
    role_id: EntityId
    permission_id: EntityId
    granted_by_user_id: EntityId
    granted_at: datetime

@dataclass
class RefreshToken(Entity):
    user_id: EntityId
    jti: str
    token_hash: str
    device_name: str | None
    ip_address: str | None
    user_agent: str | None
    issued_at: datetime
    expires_at: datetime
    revoked_at: datetime | None
    replaced_by_token_id: EntityId | None

    def is_valid(self, now: datetime) -> bool: ...   # not revoked and not expired
    def revoke(self, at: datetime, replaced_by: EntityId | None = None) -> None: ...
```

### Domain Exceptions

```python
class UserNotFoundError(EntityNotFoundError): ...
class DuplicateEmailError(UniqueConstraintViolationError): ...
class InvalidCredentialsError(BusinessRuleViolationError): ...
class UserAlreadyBlockedError(InvalidStateTransitionError): ...
class RoleAlreadyAssignedError(BusinessRuleViolationError): ...
class SystemRoleImmutableError(BusinessRuleViolationError): ...
class PermissionAlreadyGrantedError(UniqueConstraintViolationError): ...
class CannotDeleteSelfError(BusinessRuleViolationError): ...
class LastAdminCannotBeDeletedError(BusinessRuleViolationError): ...
```

### Repository Interfaces

```python
class IUserRepository(ABC):
    @abstractmethod
    def add(self, user: User) -> None: ...
    @abstractmethod
    def get_by_id(self, user_id: EntityId) -> User: ...             # raise UserNotFoundError
    @abstractmethod
    def find_by_id(self, user_id: EntityId) -> User | None: ...
    @abstractmethod
    def get_by_email(self, email: Email) -> User: ...
    @abstractmethod
    def exists_by_email(self, email: Email) -> bool: ...
    @abstractmethod
    def update(self, user: User) -> None: ...
    @abstractmethod
    def list_by_status(self, status: UserStatus, limit: int, offset: int) -> list[User]: ...
    @abstractmethod
    def list_all(self, limit: int, offset: int) -> list[User]: ...
    @abstractmethod
    def count_all(self, status: UserStatus | None = None) -> int: ...
    # list_by_status / list_all / count_all are wired to AdminListUsersUseCase for
    # real offset/limit pagination with a true total (not client-side slicing).

class IRoleRepository(ABC):
    def get_by_id(self, role_id: EntityId) -> Role: ...
    def get_by_key(self, role_key: str) -> Role: ...
    def list_all(self) -> list[Role]: ...
    def add(self, role: Role) -> None: ...

class IPermissionRepository(ABC):
    def get_by_id(self, permission_id: EntityId) -> Permission: ...
    def list_by_module(self, module: str) -> list[Permission]: ...

class IUserRoleRepository(ABC):
    def add(self, user_role: UserRole) -> None: ...
    def find_active(self, user_id: EntityId, role_id: EntityId) -> UserRole | None: ...
    def list_active_roles_for_user(self, user_id: EntityId) -> list[Role]: ...
    def list_active_user_ids_for_role(self, role_id: EntityId) -> list[EntityId]: ...
    # ^ used by the last-active-admin guard in AdminDeleteUserUseCase.
    def update(self, user_role: UserRole) -> None: ...

class IRolePermissionRepository(ABC):
    def add(self, role_permission: RolePermission) -> None: ...
    def list_permissions_for_role(self, role_id: EntityId) -> list[Permission]: ...
    def remove(self, role_id: EntityId, permission_id: EntityId) -> None: ...

class IRefreshTokenRepository(ABC):
    def add(self, token: RefreshToken) -> None: ...
    def get_by_jti(self, jti: str) -> RefreshToken: ...
    def find_by_token_hash(self, token_hash: str) -> RefreshToken | None: ...
    def update(self, token: RefreshToken) -> None: ...
    def revoke_all_for_user(self, user_id: EntityId, at: datetime) -> None: ...
```

---

## 2. Freelancer Management (`domain/freelancer`)

### Enums

- `FreelancerApprovalStatus`: `PENDING, APPROVED, REJECTED, SUSPENDED`
- `FreelancerLevelAccessType`: `STANDARD, RESTRICTED, PREMIUM`

### Entities

```python
@dataclass
class FreelancerLevel(Entity):
    level_key: str
    name: str
    rank_order: int
    access_type: FreelancerLevelAccessType
    min_completed_projects: int
    min_rating: Decimal | None
    max_active_applications: int | None
    can_apply_public_projects: bool
    can_apply_private_projects: bool
    is_active: bool

@dataclass
class FreelancerProfile(AggregateRoot):
    user_id: EntityId
    current_level_id: EntityId | None
    approval_status: FreelancerApprovalStatus
    approved_by_user_id: EntityId | None
    approved_at: datetime | None
    approval_note: str | None
    display_name: str
    headline: str | None
    bio: str | None
    country_code: str | None
    city: str | None
    timezone: str | None
    hourly_rate_min: Decimal | None
    hourly_rate_max: Decimal | None
    is_available: bool
    deleted_at: datetime | None
    created_by_user_id: EntityId | None = None
    # ^ on-behalf audit field per AUTHORIZATION.md §3.2 (defaults to the user id in the
    #   self-service case; holds the admin id in AdminCreateFreelancerProfileOnBehalfUseCase).

    def submit_for_approval(self) -> None: ...
    def approve(self, admin_id: EntityId, at: datetime, note: str | None) -> None: ...
    def reject(self, admin_id: EntityId, at: datetime, note: str) -> None: ...
    def suspend(self, admin_id: EntityId, at: datetime, note: str) -> None: ...
    def change_level(self, new_level_id: EntityId) -> None: ...
    def is_approved(self) -> bool: ...
    def set_availability(self, available: bool) -> None: ...
    def update_rate_range(self, min_rate: Decimal, max_rate: Decimal) -> None: ...

@dataclass
class FreelancerLevelHistory(Entity):
    freelancer_profile_id: EntityId
    old_level_id: EntityId | None
    new_level_id: EntityId
    assigned_by_user_id: EntityId
    reason: str | None
    assigned_at: datetime

@dataclass
class Resume(Entity):
    freelancer_profile_id: EntityId
    file_asset_id: EntityId
    version_no: int
    summary: str | None
    is_current: bool
    def mark_as_current(self) -> None: ...

@dataclass
class PortfolioItem(Entity):
    freelancer_profile_id: EntityId
    title: str
    description: str | None
    external_url: str | None
    file_asset_id: EntityId | None
    display_order: int
    is_featured: bool
    deleted_at: datetime | None
```

### Domain Exceptions

```python
class FreelancerProfileNotFoundError(EntityNotFoundError): ...
class FreelancerAlreadyApprovedError(InvalidStateTransitionError): ...
class FreelancerNotApprovedError(BusinessRuleViolationError): ...
class InvalidRateRangeError(BusinessRuleViolationError): ...
```

### Repository Interfaces

```python
class IFreelancerProfileRepository(ABC):
    def add(self, profile: FreelancerProfile) -> None: ...
    def get_by_id(self, profile_id: EntityId) -> FreelancerProfile: ...
    def get_by_user_id(self, user_id: EntityId) -> FreelancerProfile: ...
    def update(self, profile: FreelancerProfile) -> None: ...
    def list_by_approval_status(self, status: FreelancerApprovalStatus) -> list[FreelancerProfile]: ...
    def list_available_for_level(self, level_id: EntityId) -> list[FreelancerProfile]: ...

class IFreelancerLevelRepository(ABC):
    def get_by_id(self, level_id: EntityId) -> FreelancerLevel: ...
    def get_by_key(self, level_key: str) -> FreelancerLevel: ...
    def list_active(self) -> list[FreelancerLevel]: ...

class IFreelancerLevelHistoryRepository(ABC):
    def add(self, history: FreelancerLevelHistory) -> None: ...
    def list_by_profile(self, profile_id: EntityId) -> list[FreelancerLevelHistory]: ...

class IResumeRepository(ABC):
    def add(self, resume: Resume) -> None: ...
    def update(self, resume: Resume) -> None: ...
    def list_by_profile(self, profile_id: EntityId) -> list[Resume]: ...
    def get_current(self, profile_id: EntityId) -> Resume | None: ...

class IPortfolioItemRepository(ABC):
    def add(self, item: PortfolioItem) -> None: ...
    def get_by_id(self, item_id: EntityId) -> PortfolioItem: ...
    def list_by_profile(self, profile_id: EntityId) -> list[PortfolioItem]: ...
    def update(self, item: PortfolioItem) -> None: ...
    def delete(self, item_id: EntityId) -> None: ...
```

---

## 3. Category Management (`domain/category`)

### Entities

```python
@dataclass
class Category(Entity):
    parent_category_id: EntityId | None
    category_key: str
    name: str
    slug: str
    description: str | None
    is_active: bool
    sort_order: int
    deleted_at: datetime | None
    def deactivate(self) -> None: ...
    def rename(self, name: str, slug: str) -> None: ...
    def soft_delete(self, at: datetime) -> None: ...

@dataclass
class CategorySupervisor(Entity):
    category_id: EntityId
    supervisor_user_id: EntityId
    assigned_by_user_id: EntityId
    is_primary: bool
    is_active: bool
    assigned_at: datetime
    revoked_at: datetime | None
    def revoke(self, at: datetime) -> None: ...
    def promote(self) -> None: ...
        # is_primary -> True (when the primary supervisor is removed, the next active one
        # is promoted)
```

### Domain Exceptions

```python
class CategoryNotFoundError(EntityNotFoundError): ...
class DuplicateCategorySlugError(UniqueConstraintViolationError): ...
class SupervisorAlreadyAssignedError(BusinessRuleViolationError): ...
class SupervisorAssignmentNotFoundError(EntityNotFoundError): ...
```

### Repository Interfaces

```python
class ICategoryRepository(ABC):
    def add(self, category: Category) -> None: ...
    def get_by_id(self, category_id: EntityId) -> Category: ...
    def get_by_slug(self, slug: str) -> Category: ...
    def list_active(self) -> list[Category]: ...
    def update(self, category: Category) -> None: ...

class ICategorySupervisorRepository(ABC):
    def add(self, link: CategorySupervisor) -> None: ...
    def list_active_supervisors(self, category_id: EntityId) -> list[CategorySupervisor]: ...
    def list_categories_for_supervisor(self, supervisor_user_id: EntityId) -> list[EntityId]: ...
    def is_supervisor_of(self, supervisor_user_id: EntityId, category_id: EntityId) -> bool: ...
    def update(self, link: CategorySupervisor) -> None: ...
```

---

## 4. Dynamic Form Engine (`domain/form`)

### Enums

- `FormFieldType`: `TEXT, TEXTAREA, NUMBER, DECIMAL, BOOLEAN, DATE, DATETIME, EMAIL, PHONE, URL, SELECT, MULTI_SELECT, FILE, JSON`
- `FormTemplateStatus`: `DRAFT, PUBLISHED, ARCHIVED`

### Entities

```python
@dataclass
class FormFieldOption(Entity):
    option_key: str
    label: str
    value: str
    sort_order: int
    is_active: bool

@dataclass
class FormField(Entity):
    field_key: str
    label: str
    description: str | None
    field_type: FormFieldType
    is_required: bool
    is_repeatable: bool
    is_unique: bool
    sort_order: int
    validation_rules: dict | None
    options: list[FormFieldOption]
    is_active: bool
    def add_option(self, option: FormFieldOption) -> None: ...
        # rule: only for field_type in {SELECT, MULTI_SELECT}
    def change_type(self, new_type: FormFieldType) -> None: ...
    def get_option(self, option_key: str) -> FormFieldOption | None: ...

@dataclass
class FormTemplate(AggregateRoot):
    category_id: EntityId
    template_key: str
    name: str
    version_no: int
    status: FormTemplateStatus
    is_active: bool
    published_by_user_id: EntityId | None
    published_at: datetime | None
    fields: list[FormField]
    deleted_at: datetime | None

    def add_field(self, field: FormField) -> None: ...
        # rule: only when status == DRAFT
    def remove_field(self, field_id: EntityId) -> None: ...
    def publish(self, published_by: EntityId, at: datetime) -> None: ...
        # rule: must have at least one field; DRAFT -> PUBLISHED
    def new_draft_version(self, new_version_no: int, at: datetime) -> "FormTemplate": ...
    def require_draft(self, action: str) -> None: ...
```

### Domain Exceptions

```python
class FormTemplateNotFoundError(EntityNotFoundError): ...
class FieldNotFoundError(EntityNotFoundError): ...
class DuplicateFieldKeyError(UniqueConstraintViolationError): ...
class DuplicateOptionKeyError(UniqueConstraintViolationError): ...
class FormTemplateAlreadyPublishedError(InvalidStateTransitionError): ...
class FormTemplateHasNoFieldsError(BusinessRuleViolationError): ...
class InvalidFieldOptionError(BusinessRuleViolationError): ...
```

### Repository Interfaces

```python
class IFormTemplateRepository(ABC):
    def add(self, template: FormTemplate) -> None: ...
    def get_by_id(self, template_id: EntityId) -> FormTemplate: ...
    def get_published_for_category(self, category_id: EntityId) -> FormTemplate: ...
    def update(self, template: FormTemplate) -> None: ...
    def list_versions(self, category_id: EntityId) -> list[FormTemplate]: ...
```

---

## 5. Project Management (`domain/project`) — Core Domain

### Enums

```
ProjectVisibility: PUBLIC, PRIVATE, INVITE_ONLY
ProjectPriority: LOW, NORMAL, HIGH, URGENT
BudgetType: FIXED, RANGE, HOURLY, NEGOTIABLE
ProjectStatus: DRAFT, PUBLISHED, COLLECTING_APPLICATIONS, ASSIGNED, IN_PROGRESS,
               DELIVERY_SUBMITTED, UNDER_SUPERVISOR_REVIEW, REVISION_REQUESTED,
               AWAITING_CUSTOMER_REVIEW, COMPLETED, CANCELLED, REJECTED, ARCHIVED
ProjectApplicationStatus: APPLIED, SHORTLISTED, ACCEPTED, REJECTED, WITHDRAWN, EXPIRED
DeliveryStatus: SUBMITTED, UNDER_REVIEW, APPROVED, REJECTED, REVISED, SUPERSEDED
RevisionRequestStatus: OPEN, APPROVED, REJECTED, CLOSED, CANCELLED
```

### Value Objects

```python
@dataclass(frozen=True)
class Budget:
    budget_type: BudgetType
    fixed_amount: Decimal | None
    min_amount: Decimal | None
    max_amount: Decimal | None
    currency_code: str
    def __post_init__(self) -> None: ...
        # rule: fixed requires fixed_amount; range requires min<=max

@dataclass(frozen=True)
class ProjectCode:
    value: str   # e.g. "PRJ-2026-001" — format validated
```

### Entities

Project is the Aggregate Root; ProjectApplication and ProjectDelivery are separate
Aggregates referencing `project_id` to keep Aggregates small — coordination between them is
the responsibility of the Application Layer/Domain Service.

```python
@dataclass
class Project(AggregateRoot):
    project_code: ProjectCode
    customer_user_id: EntityId
    category_id: EntityId
    form_template_id: EntityId
    assigned_supervisor_user_id: EntityId | None
    selected_application_id: EntityId | None
    title: str
    description: str
    visibility: ProjectVisibility
    priority: ProjectPriority
    budget: Budget
    status: ProjectStatus
    application_deadline: datetime | None
    start_at: datetime | None
    due_at: datetime | None
    completed_at: datetime | None
    cancelled_at: datetime | None
    locked_at: datetime | None
    deleted_at: datetime | None
    created_by_user_id: EntityId | None = None
    # ^ on-behalf audit field per AUTHORIZATION.md §3.2 (self-service: equals
    #   customer_user_id; on-behalf: the admin's actor_id).

    def publish(self, at: datetime) -> None: ...
    def start_collecting_applications(self) -> None: ...
    def assign_freelancer(self, application_id: EntityId, at: datetime) -> None: ...
    def start(self, at: datetime) -> None: ...
    def mark_delivery_submitted(self) -> None: ...
    def move_to_supervisor_review(self) -> None: ...
    def move_to_customer_review(self) -> None: ...
    def request_revision(self) -> None: ...
    def complete(self, at: datetime) -> None: ...
        # sets completed_at and locked_at
    def cancel(self, at: datetime, reason: str) -> None: ...
        # sets cancelled_at and locked_at
    def is_locked(self) -> bool: ...
        # COMPLETED/CANCELLED -> locked; every mutator checks this first and raises
        # ProjectLockedError
    def can_accept_applications(self) -> bool: ...
    def has_supervisor(self) -> bool: ...
    def is_application_deadline_passed(self, at: datetime) -> bool: ...

@dataclass
class ProjectApplication(AggregateRoot):
    project_id: EntityId
    freelancer_profile_id: EntityId
    status: ProjectApplicationStatus
    cover_letter: str | None
    proposed_amount: Decimal | None
    proposed_days: int | None
    applied_at: datetime
    decided_by_user_id: EntityId | None
    decided_at: datetime | None
    decision_note: str | None
    withdrawn_at: datetime | None
    submitted_by_user_id: EntityId | None = None
        # audit: who actually submitted the application (may differ from
        # freelancer_profile_id's owning user on the admin on-behalf path)

    def shortlist(self) -> None: ...
    def accept(self, decided_by: EntityId, at: datetime) -> None: ...
    def reject(self, decided_by: EntityId, at: datetime, note: str | None) -> None: ...
    def withdraw(self, at: datetime) -> None: ...

@dataclass
class ProjectDelivery(AggregateRoot):
    project_id: EntityId
    version_no: int
    submitted_by_user_id: EntityId
    status: DeliveryStatus
    delivery_note: str | None
    submitted_at: datetime
    reviewed_at: datetime | None
    reviewer_user_id: EntityId | None
    superseded_by_delivery_id: EntityId | None
    file_asset_ids: list[EntityId]

    def mark_under_review(self) -> None: ...
    def approve(self, reviewer_id: EntityId, at: datetime) -> None: ...
    def reject(self, reviewer_id: EntityId, at: datetime) -> None: ...
    def mark_revised(self) -> None: ...
    def supersede(self, new_delivery_id: EntityId) -> None: ...

@dataclass
class ProjectRevisionRequest(Entity):
    project_id: EntityId
    project_delivery_id: EntityId | None
    requested_by_user_id: EntityId
    requested_to_user_id: EntityId | None
    round_no: int
    status: RevisionRequestStatus
    reason: str
    resolved_by_user_id: EntityId | None
    requested_at: datetime
    resolved_at: datetime | None

    def close(self, resolved_by: EntityId, at: datetime) -> None: ...

@dataclass
class ProjectStatusHistory(Entity):
    project_id: EntityId
    from_status: ProjectStatus | None
    to_status: ProjectStatus
    changed_by_user_id: EntityId
    reason: str | None
    changed_at: datetime
```

### Domain Services (`domain/project/services.py`)

```python
class RevisionPolicy:
    MAX_REVISIONS = 3
    @staticmethod
    def can_request_new_revision(existing_requests: list[ProjectRevisionRequest]) -> bool:
        return len(existing_requests) < RevisionPolicy.MAX_REVISIONS
    @staticmethod
    def ensure_can_request_new_revision(existing_requests: list[ProjectRevisionRequest]) -> None:
        # raises MaxRevisionsExceededError if at the cap
        ...

class FreelancerEligibilityPolicy:
    @staticmethod
    def is_eligible_to_apply(
        level: "FreelancerLevel", project: Project, active_application_count: int
    ) -> bool: ...
        # returns False if level is inactive
        # checks can_apply_public/private_projects and max_active_applications
```

### Domain Exceptions

```python
class ProjectNotFoundError(EntityNotFoundError): ...
class ProjectLockedError(BusinessRuleViolationError): ...
class ProjectAlreadyAssignedError(BusinessRuleViolationError): ...
class InvalidProjectStatusTransitionError(InvalidStateTransitionError): ...
class ApplicationNotFoundError(EntityNotFoundError): ...
class ApplicationAlreadyDecidedError(InvalidStateTransitionError): ...
class DuplicateApplicationError(UniqueConstraintViolationError): ...
class DeliveryNotFoundError(EntityNotFoundError): ...
class MaxRevisionsExceededError(BusinessRuleViolationError): ...
class FreelancerNotEligibleError(BusinessRuleViolationError): ...
class ApplicationDeadlineExpiredError(BusinessRuleViolationError): ...
class InvalidBudgetError(BusinessRuleViolationError): ...
class InvalidProjectCodeError(BusinessRuleViolationError): ...
```

### Repository Interfaces

```python
class IProjectRepository(ABC):
    def add(self, project: Project) -> None: ...
    def get_by_id(self, project_id: EntityId) -> Project: ...
    def get_by_code(self, project_code: ProjectCode) -> Project: ...
    def update(self, project: Project) -> None: ...
    def list_by_customer(self, customer_user_id: EntityId, status: ProjectStatus | None = None) -> list[Project]: ...
    def list_available_for_freelancer(self, level_id: EntityId) -> list[Project]: ...
    def list_by_supervisor(self, supervisor_user_id: EntityId) -> list[Project]: ...
    def list_by_category(self, category_id: EntityId) -> list[Project]: ...

class IProjectApplicationRepository(ABC):
    def add(self, application: ProjectApplication) -> None: ...
    def get_by_id(self, application_id: EntityId) -> ProjectApplication: ...
    def find_by_project_and_freelancer(self, project_id: EntityId, freelancer_profile_id: EntityId) -> ProjectApplication | None: ...
    def list_by_project(self, project_id: EntityId) -> list[ProjectApplication]: ...
    def count_active_for_freelancer(self, freelancer_profile_id: EntityId) -> int: ...
    def update(self, application: ProjectApplication) -> None: ...

class IProjectDeliveryRepository(ABC):
    def add(self, delivery: ProjectDelivery) -> None: ...
    def get_by_id(self, delivery_id: EntityId) -> ProjectDelivery: ...
    def get_latest_for_project(self, project_id: EntityId) -> ProjectDelivery | None: ...
    def list_by_project(self, project_id: EntityId) -> list[ProjectDelivery]: ...
    def update(self, delivery: ProjectDelivery) -> None: ...

class IProjectRevisionRequestRepository(ABC):
    def add(self, revision: ProjectRevisionRequest) -> None: ...
    def list_by_project(self, project_id: EntityId) -> list[ProjectRevisionRequest]: ...
    def count_by_project(self, project_id: EntityId) -> int: ...
    def update(self, revision: ProjectRevisionRequest) -> None: ...

class IProjectStatusHistoryRepository(ABC):
    def add(self, history: ProjectStatusHistory) -> None: ...
    def list_by_project(self, project_id: EntityId) -> list[ProjectStatusHistory]: ...
```

---

## 6. Quality Assurance / Supervisor Review (`domain/review`)

### Enums

- `ReviewStatus`: `PENDING, APPROVED, REJECTED`

### Entities

```python
@dataclass
class SupervisorReview(Entity):
    project_delivery_id: EntityId
    project_id: EntityId
    supervisor_user_id: EntityId
    decision: ReviewStatus
    reject_reason: str | None
    notes: str | None
    reviewed_at: datetime

    def approve(self, notes: str | None) -> None: ...
    def reject(self, reason: str) -> None: ...
```

### Domain Exceptions

```python
class SupervisorReviewNotFoundError(EntityNotFoundError): ...
class NotAssignedSupervisorError(BusinessRuleViolationError): ...
class DeliveryAlreadyReviewedError(InvalidStateTransitionError): ...
```

### Repository Interface

```python
class ISupervisorReviewRepository(ABC):
    def add(self, review: SupervisorReview) -> None: ...
    def get_by_delivery(self, project_delivery_id: EntityId) -> SupervisorReview: ...
    def find_by_delivery(self, project_delivery_id: EntityId) -> SupervisorReview | None: ...
    def list_pending_for_supervisor(self, supervisor_user_id: EntityId) -> list[SupervisorReview]: ...
    def update(self, review: SupervisorReview) -> None: ...
```

---

## 7. Feedback & Rating (`domain/feedback`)

### Entities

```python
@dataclass
class CustomerReview(Entity):
    project_id: EntityId
    project_delivery_id: EntityId
    customer_user_id: EntityId
    decision: ReviewStatus     # reused from review.enums
    comment: str | None
    reviewed_at: datetime

@dataclass
class Rating(Entity):
    customer_review_id: EntityId
    project_id: EntityId
    customer_user_id: EntityId
    freelancer_profile_id: EntityId
    score: int              # 1..5
    comment: str | None
    is_public: bool

    def __post_init__(self) -> None:
        if not (1 <= self.score <= 5):
            raise InvalidRatingScoreError(...)
```

### Domain Exceptions

```python
class InvalidRatingScoreError(BusinessRuleViolationError): ...
class RatingAlreadyExistsError(UniqueConstraintViolationError): ...
class ProjectNotCompletedError(BusinessRuleViolationError): ...
```

> **Verify before Phase 2**: confirm whether `CustomerReviewNotApprovedError` (used by
> `SubmitRatingUseCase` to enforce that the referenced `CustomerReview.decision ==
APPROVED`) has been added here.

### Repository Interfaces

```python
class ICustomerReviewRepository(ABC):
    def add(self, review: CustomerReview) -> None: ...
    def find_by_project(self, project_id: EntityId) -> CustomerReview | None: ...

class IRatingRepository(ABC):
    def add(self, rating: Rating) -> None: ...
    def find_by_project(self, project_id: EntityId) -> Rating | None: ...
    def list_by_freelancer(self, freelancer_profile_id: EntityId) -> list[Rating]: ...
    def average_score_for_freelancer(self, freelancer_profile_id: EntityId) -> Decimal | None: ...
```

---

## 8. Communication / Ticketing (`domain/ticketing`)

### Enums

```
TicketStatus: OPEN, IN_PROGRESS, WAITING_CUSTOMER, WAITING_FREELANCER,
              WAITING_SUPERVISOR, CLOSED, ARCHIVED
TicketPriority: LOW, NORMAL, HIGH, URGENT
TicketMessageType: TEXT, FILE, SYSTEM
TicketParticipantRole: REQUESTER, ASSIGNEE, WATCHER, SUPERVISOR, ADMIN, CUSTOMER, FREELANCER
```

### Entities

```python
@dataclass
class Ticket(AggregateRoot):
    ticket_code: str
    created_by_user_id: EntityId
    assigned_to_user_id: EntityId | None
    related_project_id: EntityId | None
    related_category_id: EntityId | None
    subject: str
    status: TicketStatus
    priority: TicketPriority
    closed_by_user_id: EntityId | None
    closed_at: datetime | None
    last_message_at: datetime | None
    deleted_at: datetime | None
    submitted_by_user_id: EntityId | None = None
    # ^ on-behalf audit field per AUTHORIZATION.md §3.2 (created_by_user_id holds the
    #   target/requester; this field records the admin when created on their behalf).

    def assign(self, user_id: EntityId) -> None: ...
    def close(self, by_user_id: EntityId, at: datetime) -> None: ...
    def touch_last_message(self, at: datetime) -> None: ...
    def is_closed(self) -> bool: ...

@dataclass
class TicketParticipant(Entity):
    ticket_id: EntityId
    user_id: EntityId
    participant_role: TicketParticipantRole
    joined_at: datetime
    left_at: datetime | None

@dataclass
class TicketMessage(Entity):
    ticket_id: EntityId
    sender_user_id: EntityId
    message_type: TicketMessageType
    body: str | None
    is_internal: bool
    sent_at: datetime
    edited_at: datetime | None
    deleted_at: datetime | None
    attachment_file_asset_ids: list[EntityId]
```

### Domain Exceptions

```python
class TicketNotFoundError(EntityNotFoundError): ...
class TicketClosedError(BusinessRuleViolationError): ...
class NotTicketParticipantError(BusinessRuleViolationError): ...
```

### Repository Interfaces

```python
class ITicketRepository(ABC):
    def add(self, ticket: Ticket) -> None: ...
    def get_by_id(self, ticket_id: EntityId) -> Ticket: ...
    def get_by_code(self, ticket_code: str) -> Ticket: ...
    def list_for_user(self, user_id: EntityId) -> list[Ticket]: ...
    def update(self, ticket: Ticket) -> None: ...

class ITicketMessageRepository(ABC):
    def add(self, message: TicketMessage) -> None: ...
    def list_by_ticket(self, ticket_id: EntityId) -> list[TicketMessage]: ...

class ITicketParticipantRepository(ABC):
    def add(self, participant: TicketParticipant) -> None: ...
    def list_by_ticket(self, ticket_id: EntityId) -> list[TicketParticipant]: ...
    def is_participant(self, ticket_id: EntityId, user_id: EntityId) -> bool: ...
```

---

## 9. Reporting & Analytics (`domain/reporting`) — Read-Only

This context has only a Read Model and a Query Repository; no mutable Entity (no write
side). Outputs are simple dataclasses (not Aggregates):

```python
@dataclass(frozen=True)
class DashboardStatistics:
    total_users: int
    active_projects: int
    total_freelancers: int
    total_revenue: Decimal

@dataclass(frozen=True)
class ProjectStatistics:
    created: int
    completed: int
    cancelled: int

class IReportingReadRepository(ABC):
    def get_dashboard_statistics(self) -> DashboardStatistics: ...
    def get_user_statistics(self) -> "UserStatistics": ...
    def get_project_statistics(self) -> ProjectStatistics: ...
    def get_freelancer_statistics(self) -> "FreelancerStatistics": ...
    def get_customer_statistics(self) -> "CustomerStatistics": ...
```

Because this context is purely Query/Aggregation over other contexts' data, its Phase 2
repository implementation may join directly across several tables.

---

## 10. Cross-Context Business Rules

These must be implemented at the Entity/Domain Service level (not only in application):

1. A Project has at most one `selected_application_id` → `Project.assign_freelancer`.
2. A Supervisor only sees projects in their own Category →
   `ICategorySupervisorRepository.is_supervisor_of`, feeding the two-tier
   `review.decide_own`/`review.decide_any` check (`AUTHORIZATION.md`).
3. A Freelancer may only apply to projects matching their level →
   `FreelancerEligibilityPolicy`.
4. Maximum Revision count = 3 → `RevisionPolicy`, enforced on every revision-creating path.
5. A Completed project is immutable → `Project.is_locked()` checked in every mutator.
6. Rating is only allowed after Completion → checked via `project.status == COMPLETED` at
   the Application layer + `ProjectNotCompletedError`.
7. Only Admin can Approve a Freelancer → an Authorization rule, not a Domain rule; checked
   via `IAuthorizationService` in `application`.
8. Reporting is Read-Only → no mutable Entity/Aggregate in this context.
9. Owned-resource mutations use the two-tier `_own`/`_any` convention; creation-on-behalf
   uses the Self vs. On-Behalf Pattern B split — see `AUTHORIZATION.md` for both.
