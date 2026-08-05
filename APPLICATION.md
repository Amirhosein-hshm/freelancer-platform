# APPLICATION.md — Application Layer Specification

> **Phase 2 note:** as of Phase 2, this entire layer is **async**. Every `UseCase.execute`,
> every `IUnitOfWork` context-manager method, and every port/repository method called from a
> use case is `async def` and `await`ed. This file's code samples below show the async form;
> if you find an older sync signature anywhere in this document or in the codebase, treat it
> as stale and update it — sync and async must not be mixed within the `application` layer.

## 1. Base Use Case Pattern

```python
# application/shared/use_case.py
TRequest = TypeVar("TRequest")
TResponse = TypeVar("TResponse")

class UseCase(ABC, Generic[TRequest, TResponse]):
    @abstractmethod
    async def execute(self, request: TRequest) -> TResponse: ...
```

Every Use Case:

- Takes one input Command/Query DTO (`frozen dataclass`).
- Returns one output Result DTO (`frozen dataclass`).
- Only works with `domain` Interfaces (Repository) and `application/shared/ports.py`
  (Service) — never directly depends on `infrastructure` (injected via constructor).
- Delegates state-machine/business-rule logic to the Entity/Domain Service and only
  performs orchestration + exception translation itself.

## 2. Shared Ports (`application/shared/ports.py`)

```python
class IPasswordHasher(ABC):
    @abstractmethod
    async def hash(self, plain_password: str) -> str: ...
    @abstractmethod
    async def verify(self, plain_password: str, hashed: str) -> bool: ...

class ITokenService(ABC):
    @abstractmethod
    async def generate_access_token(self, user_id: EntityId, roles: list[str]) -> str: ...
    @abstractmethod
    async def generate_refresh_token(self) -> tuple[str, str]: ...
        # -> (raw_token, jti) — raw is given to the user only once, only its hash is stored
    @abstractmethod
    async def hash_refresh_token(self, raw_token: str) -> str: ...
    @abstractmethod
    async def decode_access_token(self, token: str) -> "AccessTokenPayload": ...
        # raise InvalidTokenError / ExpiredTokenError

@dataclass(frozen=True)
class AccessTokenPayload:
    user_id: EntityId
    roles: list[str]
    expires_at: datetime

class IClock(ABC):
    @abstractmethod
    def now(self) -> datetime: ...
        # sync is fine — no I/O

class IIdGenerator(ABC):
    @abstractmethod
    def new_id(self) -> EntityId: ...
        # sync is fine — no I/O

class IUnitOfWork(ABC):
    """Transaction control for use cases that mutate multiple Aggregates/Repositories."""
    @abstractmethod
    async def __aenter__(self) -> "IUnitOfWork": ...
    @abstractmethod
    async def __aexit__(self, exc_type, exc, tb) -> None: ...
    @abstractmethod
    async def commit(self) -> None: ...
    @abstractmethod
    async def rollback(self) -> None: ...

class IEventPublisher(ABC):   # re-exported/re-defined from domain.shared.events
    @abstractmethod
    async def publish(self, events: list["DomainEvent"]) -> None: ...

class INotificationService(ABC):
    @abstractmethod
    async def send_email(self, to: str, subject: str, body: str) -> None: ...
    @abstractmethod
    async def send_verification_email(self, to: str, token: str) -> None: ...
    @abstractmethod
    async def send_password_reset_email(self, to: str, token: str) -> None: ...

class IFileStorageService(ABC):
    @abstractmethod
    async def get_metadata(self, file_asset_id: EntityId) -> "FileAssetMetadata": ...
    @abstractmethod
    async def register_uploaded_file(self, ...) -> EntityId: ...

class IProjectCodeGenerator(ABC):
    @abstractmethod
    async def next_code(self, year: int) -> str: ...

class ITicketCodeGenerator(ABC):
    @abstractmethod
    async def next_code(self, year: int) -> str: ...
```

```python
# application/shared/authorization.py
class IAuthorizationService(ABC):
    @abstractmethod
    async def has_permission(self, user_id: EntityId, permission_key: str) -> bool: ...
    @abstractmethod
    async def require_permission(self, user_id: EntityId, permission_key: str) -> None: ...
        # raise PermissionDeniedError
    @abstractmethod
    async def has_role(self, user_id: EntityId, role_key: str) -> bool: ...

def authorize_owned_action(...) -> Awaitable[None]:
    # see AUTHORIZATION.md §3.1 — also async: `await authorize_owned_action(...)`
    ...
```

This Interface lets the rule "only Admin can do X" be checked in one line in every Use
Case without duplicating RBAC logic everywhere. Its real implementation (a join over
`user_roles`/`role_permissions`) lives in `infrastructure` (Phase 2) per the RBAC
data-source contract in `AUTHORIZATION.md` §6; in tests, a simple async Fake is used.

## 3. Per-Context Organization in `application`

```
application/<context>/
├── dto.py            # Command/Query + Result dataclasses
├── permissions.py     # PERMISSION_* string constants used by this context's use cases
├── exceptions.py       # Application-level exceptions (non-Domain errors)
└── use_cases/
    └── <use_case_name>.py   # each Use Case in its own file, one class
```

---

## 4. IAM — Use Cases (Phase 1, Core + Hardening)

### RegisterUser

```python
@dataclass(frozen=True)
class RegisterUserCommand:
    email: str
    password: str
    first_name: str
    last_name: str

@dataclass(frozen=True)
class RegisterUserResult:
    user_id: EntityId
    email: str
    status: str
    created_at: datetime

class RegisterUserUseCase(UseCase[RegisterUserCommand, RegisterUserResult]):
    def __init__(
        self,
        user_repo: IUserRepository,
        user_role_repo: IUserRoleRepository,
        role_repo: IRoleRepository,
        password_hasher: IPasswordHasher,
        id_generator: IIdGenerator,
        clock: IClock,
        notification_service: INotificationService,
        uow: IUnitOfWork,
    ) -> None: ...

    async def execute(self, request: RegisterUserCommand) -> RegisterUserResult:
        # 1. request.validate()
        # 2. Email(request.email) -> InvalidEmailError on bad format
        # 3. await user_repo.exists_by_email(...) -> DuplicateEmailError if taken
        # 4. await role_repo.get_by_key("customer") -> RoleNotFoundError if not seeded
        # 5. hash password; build User(status=PENDING)
        # 6. build UserRole(assigned_by_user_id=user.id, assigned_at=now)
        # 7. async with self._uow: await user_repo.add(user); await user_role_repo.add(role); await uow.commit()
        # 8. await notification_service.send_verification_email(...) (after commit)
        ...
```

Expected errors: `ValidationError`, `InvalidEmailError`, `DuplicateEmailError`,
`RoleNotFoundError` → mapped to HTTP by `presentation` per `ERROR_HANDLING.md`.

### LoginUser

Input: email/password. Flow: `await user_repo.get_by_email` — a missing user is converted
to `InvalidCredentialsError` (not `UserNotFoundError`, to prevent email enumeration) →
`await password_hasher.verify` → `not user.is_active()` (checks status **and**
`deleted_at`) → `UserNotActiveError` → generate access/refresh token → `await
refresh_token_repo.add(...)` → `await user_repo.update` (`record_login`).

### LogoutUser

Input: `refresh_token_jti`. Flow: find token → `revoke()` → update.

### RefreshToken

Input: `raw_refresh_token`. Flow: hash the raw token → find by hash → `is_valid(now)` else
`InvalidRefreshTokenError` → issue new access token → mandatory rotation: issue new refresh
token, revoke the old one with `replaced_by_token_id`.

### ChangePassword / ForgotPassword

`ChangePasswordUseCase(user_id, old_password, new_password)`: verify old password → hash
new → `user.change_password(...)` → update.
`ForgotPasswordUseCase(email)`: to prevent user enumeration, a reset token is generated and
emailed **only if** `await exists_by_email(email)` is true; either way the same success
result is returned.

### BlockUser / ActivateUser

Requires `authorization_service.require_permission(actor_id, "user.block")` /
`"user.activate"`. Flow: `get_by_id` → `user.block(...)`/`activate()` → `update`.

### AssignRole / RemoveRole

`AssignRoleUseCase(actor_id, target_user_id, role_key)`: `require_permission("user.assign_role")`
→ role = `role_repo.get_by_key` → if `user_role_repo.find_active` exists →
`RoleAlreadyAssignedError` → new `UserRole` → `add`.
`RemoveRoleUseCase`: `require_permission("user.remove_role")` → role = `get_by_key` → if
`role.is_system` → `SystemRoleImmutableError` → if no active link →
`UserRoleNotFoundError`.

### GrantPermission / RevokePermission

`GrantPermissionUseCase`: `require_permission("user.grant_permission")` → role =
`role_repo.get_by_id`, permission = `permission_repo.get_by_id` → if already granted
(`list_permissions_for_role`) → `PermissionAlreadyGrantedError` → new `RolePermission` →
`add`.
`RevokePermissionUseCase`: `require_permission("user.revoke_permission")` → role =
`role_repo.get_by_id`; if `role.is_system` → `SystemRoleImmutableError` →
`permission_repo.get_by_id` (existence check) → `role_permission_repo.remove`.

### Admin User CRUD

- `AdminCreateUserUseCase` — `require_permission("user.create")`; creates a user directly
  with `status=ACTIVE` (explicit documented difference from self-registration's `PENDING`),
  reusing the duplicate-email check.
- `AdminUpdateUserUseCase` — `require_permission("user.update_any")`; edits identity fields
  only, never `status`.
- `AdminDeleteUserUseCase` — `require_permission("user.delete")`; calls
  `User.soft_delete(at)`; guards against self-deletion (`CannotDeleteSelfError`) and against
  deleting the last active admin (`LastAdminCannotBeDeletedError`).

> **Verify before relying on this section**: confirm the actual current signatures of these
> three use cases and their DTOs in the codebase before building `presentation` endpoints
> against them — this document may lag the implementation.

---

## 5. Freelancer — Use Cases (Phase 1)

- `CreateFreelancerProfileUseCase(user_id, display_name, ...)` — checks no existing profile →
  `FreelancerProfile(approval_status=PENDING)` → `add`. Requires
  `require_permission(request.user_id, "freelancer.create_own")`.
- `AdminCreateFreelancerProfileOnBehalfUseCase` — Pattern B counterpart, requires
  `"freelancer.create_on_behalf"`, shares core logic via a private helper, verifies the
  target user exists first.
- `UpdateFreelancerProfileUseCase` — `get_by_user_id` → allowed fields (`bio`, `city`,
  `hourly_rate_*` via `update_rate_range`) → `update`.
- `UploadResumeUseCase(profile_id, file_asset_id, summary)` — `file_storage.get_metadata` to
  confirm the file exists → new `Resume(version_no=last+1, is_current=True)` → previous
  version demoted → `add`/`update`.
- `AddPortfolioItemUseCase` / `UpdatePortfolioItemUseCase` / `DeletePortfolioItemUseCase` —
  ownership-mismatch branches raise `PermissionDeniedError` (see `AUTHORIZATION.md` §5
  hide-vs-deny policy), not `PortfolioItemNotFoundError`.
- `SubmitFreelancerApprovalUseCase(profile_id)` → `profile.submit_for_approval()` → `update`.
- `ApproveFreelancerUseCase(actor_id, profile_id, note)` — `require_permission
("freelancer.approve")` → `profile.approve(actor_id, now, note)` → `update` + initial
  `FreelancerLevelHistory` if a default level is granted.
- `RejectFreelancerUseCase(actor_id, profile_id, note)`.
- `AssignFreelancerLevelUseCase(actor_id, profile_id, new_level_id, reason)` —
  `level_repo.get_by_id` (existence) → `profile.change_level(...)` →
  `FreelancerLevelHistory` recorded → `update`.
- `GetFreelancerProfileUseCase(profile_id)` — plain read query.
- `GetFreelancerStatisticsUseCase(profile_id)` — implemented via `IReportingReadRepository`
  (not direct cross-repository aggregation).

---

## 6. Category — Use Cases (Phase 1)

- `CreateCategoryUseCase` / `UpdateCategoryUseCase` / `DeleteCategoryUseCase` (soft delete) —
  require `"category.manage"`.
- `AssignSupervisorUseCase(actor_id, category_id, supervisor_user_id)` — require
  `"category.assign_supervisor"` → verifies both the category and the supervisor user exist
  → checks not already active → new `CategorySupervisor` → `add`.
- `RemoveSupervisorUseCase` — require `"category.remove_supervisor"`; if the removed
  supervisor was primary, promotes the next active supervisor (`CategorySupervisor.promote()`).
- `GetCategoriesUseCase` / `GetCategoryProjectsUseCase` (implemented once `IProjectRepository`
  existed; uses it to list a category's projects).

---

## 7. Dynamic Form Engine — Use Cases (Phase 1)

- `CreateFormTemplateUseCase(category_id, name, template_key)` — require `"form.manage"` →
  first `FormTemplate(version_no=1, status=DRAFT)`.
- `UpdateFormTemplateUseCase` (only while DRAFT).
- `PublishFormTemplateUseCase(template_id, published_by)` — require `"form.manage"` →
  `template.publish(...)` (errors if no fields) → `update`.
- `AddFieldUseCase` / `UpdateFieldUseCase` / `RemoveFieldUseCase`.
- `AddFieldOptionUseCase` (SELECT/MULTI_SELECT only — domain `InvalidFieldOptionError`
  otherwise).
- `GetFormTemplateUseCase(category_id)` → `get_published_for_category`.

---

## 8. Project Management — Use Cases (Phase 1, most important section)

### CreateProject (self-service — Pattern B)

```python
@dataclass(frozen=True)
class CreateProjectCommand:
    actor_id: EntityId            # also the project's customer_user_id (self-service)
    category_id: EntityId
    title: str
    description: str
    visibility: str
    budget_type: str
    fixed_budget: Decimal | None
    budget_min: Decimal | None
    budget_max: Decimal | None
    currency_code: str
    application_deadline: datetime | None
    form_values: list["FormValueInput"]   # field_id, value

class CreateProjectUseCase(UseCase[CreateProjectCommand, ProjectResult]):
    # deps: IAuthorizationService, IProjectRepository, ICategoryRepository,
    #       IFormTemplateRepository, IProjectStatusHistoryRepository,
    #       IProjectCodeGenerator, IIdGenerator, IClock, IUnitOfWork
    async def execute(self, request: CreateProjectCommand) -> ProjectResult:
        await self._authz.require_permission(request.actor_id, "project.create_own")
        return await _create_project(
            customer_user_id=request.actor_id,
            created_by_user_id=request.actor_id,
            category_id=request.category_id, ...,
        )
```

### AdminCreateProjectOnBehalfUseCase (Pattern B — on-behalf counterpart)

```python
@dataclass(frozen=True)
class CreateProjectOnBehalfCommand:
    actor_id: EntityId
    target_customer_user_id: EntityId
    category_id: EntityId
    ...  # same remaining fields as CreateProjectCommand

class AdminCreateProjectOnBehalfUseCase(UseCase[CreateProjectOnBehalfCommand, ProjectResult]):
    async def execute(self, request: CreateProjectOnBehalfCommand) -> ProjectResult:
        await self._authz.require_permission(request.actor_id, "project.create_on_behalf")
        await self._user_repo.get_by_id(request.target_customer_user_id)  # UserNotFoundError if missing
        return await _create_project(
            customer_user_id=request.target_customer_user_id,
            created_by_user_id=request.actor_id,
            category_id=request.category_id, ...,
        )
```

Both call a shared private helper `_create_project(...)` (category/form-template lookup,
form validation, project-code generation, `Budget`/`Project` construction, persistence,
status-history recording) — the only difference between the two callers is `customer_user_id`
vs. `created_by_user_id` and which permission is checked.

> **Verify before relying on this section**: confirm whether this self-service/on-behalf
> split (and the `Project.created_by_user_id` audit field it depends on) is actually present
> in the current codebase — this was an agreed fix that may or may not have been executed
> yet; do not assume.

### PublishProject

`publish(now)` immediately followed by `start_collecting_applications()` in the same
operation (two history rows) — see the entity docstring for why the two statuses are kept
distinct even though the transition is atomic here. Authorization:
`authorize_owned_action(actor_id, project.customer_user_id, "project.manage_own",
"project.manage_any")`.

### CancelProject / StartProject / CompleteProject / AcceptFreelancer / RejectFreelancer /

### RequestRevision / ViewApplications

All use `authorize_owned_action(authz, actor_id, project.customer_user_id,
"project.manage_own", "project.manage_any")` (Pattern A) as their first step.
`RequestRevision` additionally calls `RevisionPolicy.ensure_can_request_new_revision(...)`
before creating a new `ProjectRevisionRequest`, capturing `from_status` **before** mutating
the project (so the status-history row is accurate).

### ApplyForProject (self-service — Pattern A on the read side, permission-gated)

0. `await authorization_service.require_permission(actor_id, "project.apply")`.
1. `project = await project_repo.get_by_id` → `project.can_accept_applications()`.
2. `project.is_application_deadline_passed(now)` → `ApplicationDeadlineExpiredError`.
3. `profile = await freelancer_profile_repo.get_by_user_id(actor_id)` →
   `profile.is_approved()` else `FreelancerNotApprovedError`.
4. Duplicate check via `find_by_project_and_freelancer` → `DuplicateApplicationError`.
5. Load level; `count_active_for_freelancer`;
   `FreelancerEligibilityPolicy.is_eligible_to_apply(...)` else `FreelancerNotEligibleError`.
6. New `ProjectApplication(status=APPLIED, submitted_by_user_id=actor_id)` → `add`.

### AdminApplyForProjectOnBehalfUseCase (Pattern B)

Requires `"project.apply_on_behalf"`; takes `target_freelancer_profile_id` instead of
deriving the profile from `actor_id`; shares the eligibility/duplicate-check core logic with
`ApplyForProjectUseCase` via a private helper; sets `submitted_by_user_id = actor_id` (the
admin), `freelancer_profile_id = target_freelancer_profile_id` (the real owner).

### WithdrawApplication

Ownership mismatch → `PermissionDeniedError` (hide-vs-deny policy, `AUTHORIZATION.md` §5).

### SubmitDelivery

Actor must be the selected freelancer of the project. Versioned; supersedes the previous
delivery if the project was in `REVISION_REQUESTED`. Routes to
`move_to_supervisor_review()` (pre-creating a PENDING `SupervisorReview`) if the project has
a supervisor, else `move_to_customer_review()`.

### GetProjectDetails / GetMyProjects / GetAvailableProjects

Read queries; `GetAvailableProjects` requires the freelancer to be approved and uses
`list_available_for_freelancer` (level-gated filter implemented in the repository).

---

## 9. Quality Assurance / Supervisor Review — Use Cases (Phase 1)

- `GetSupervisorProjectsUseCase(supervisor_user_id)` → `project_repo.list_by_supervisor`.
- `GetPendingReviewsUseCase(supervisor_user_id)` →
  `supervisor_review_repo.list_pending_for_supervisor`.
- `ReviewDeliveryUseCase` / `ApproveDeliveryUseCase` / `RejectDeliveryUseCase` (all three
  share `decide_delivery_review(...)` in `review/use_cases/review_workflow.py`):
  1. Load delivery + project.
  2. Status guard: `project.status == UNDER_SUPERVISOR_REVIEW` else
     `InvalidStateTransitionError`.
  3. Two-tier authorization: if `category_supervisor_repo.is_supervisor_of(actor_id,
project.category_id)` → require `"review.decide_own"`; else require
     `"review.decide_any"` (admin bypass).
  4. Reuse the existing PENDING `SupervisorReview` (created by `SubmitDelivery`) or build a
     new one; already-decided → `DeliveryAlreadyReviewedError`.
  5. On reject: `RevisionPolicy.ensure_can_request_new_revision(...)` (3-round cap enforced
     here too) before creating the `ProjectRevisionRequest`.
  6. Persist the review via `update` (reused) or `add` (new) — never `add` on a
     pre-existing row.

---

## 10. Feedback & Rating — Use Cases (Phase 1)

- `SubmitReviewUseCase(actor_id, project_id, decision, comment)` —
  `authorize_owned_action(..., "feedback.manage_own", "feedback.manage_any")`; requires
  `project.status == AWAITING_CUSTOMER_REVIEW`; on `APPROVED` → `Project.complete`; on
  `REJECTED` → `RevisionPolicy.ensure_can_request_new_revision(...)` then create a
  `ProjectRevisionRequest` and `request_revision()`.
- `SubmitRatingUseCase(actor_id, project_id, score, comment, is_public)` —
  `authorize_owned_action(..., "feedback.manage_own", "feedback.manage_any")`; requires
  `project.status == COMPLETED`; requires the related `CustomerReview.decision ==
ReviewStatus.APPROVED` before allowing the rating; one rating per project
  (`RatingAlreadyExistsError`).
- `GetFreelancerRatingsUseCase` / `GetProjectRatingUseCase` — read queries.

---

## 11. Communication / Ticketing — Use Cases (Phase 1)

- `CreateTicketUseCase(actor_id, subject, related_project_id, priority)` →
  `Ticket(status=OPEN)` + `TicketParticipant(role=REQUESTER)` → `add`.
- `AdminCreateTicketOnBehalfUseCase` (Pattern B) — requires `"ticket.create_on_behalf"`,
  takes a `target_user_id`, verifies the target exists, shares core logic with
  `CreateTicketUseCase` via a private helper.
- `AssignTicketUseCase(actor_id, ticket_id, assignee_user_id)` — requires
  `"ticket.assign"`.
- `SendMessageUseCase(actor_id, ticket_id, body, attachments)` — `ticket.is_closed()` →
  `TicketClosedError`, else record message + `touch_last_message`.
- `GetTicketMessagesUseCase` / `GetUserTicketsUseCase` (latter:
  `authorize_owned_action(authz, actor_id, user_id, "ticket.read_own", "ticket.read_any")`).
- `CloseTicketUseCase(actor_id, ticket_id)` —
  `authorize_owned_action(authz, actor_id, ticket.created_by_user_id, "ticket.close_own",
"ticket.close_any")` + participant check → `ticket.close(actor_id, now)`.

---

## 12. Reporting & Analytics — Use Cases (Phase 1, Read-Only)

- `GetDashboardStatisticsUseCase`, `GetUserStatisticsUseCase`, `GetProjectStatisticsUseCase`,
  `GetFreelancerStatisticsUseCase`, `GetCustomerStatisticsUseCase`,
  `GetSystemAnalyticsUseCase` — all require `"reporting.read"` and delegate directly to
  `IReportingReadRepository`; no write logic.

---

## 13. Application-Level Exceptions (`application/shared/exceptions.py`)

Separate from Domain Exceptions because they relate to orchestration/authorization, not an
Entity's own rule (full detail in `ERROR_HANDLING.md`):

```python
class ApplicationError(Exception): ...
class PermissionDeniedError(ApplicationError): ...
class ValidationError(ApplicationError): ...
class FormValidationError(ValidationError): ...
class ExternalServiceError(ApplicationError): ...   # when an external Port fails
```

## 14. Wiring/Composition — Now Implemented (see `PRESENTATION.md`/`INFRASTRUCTURE.md`)

In Phase 2, the Composition Root (`bootstrap/container.py` — **not**
`presentation/core/container.py**) fills every Port/Repository with its real
`infrastructure`implementation and injects it into Use Cases via FastAPI's`app.dependency_overrides`, keeping `presentation`free of any`infrastructure`import (see`ARCHITECTURE.md`§1 and`PRESENTATION.md`§3). In tests, Fakes continue to play this role
(see`TESTING.md`).
