# APPLICATION.md — مشخصات لایه Application

## 1. الگوی پایه Use Case

```python
# application/shared/use_case.py
TRequest = TypeVar("TRequest")
TResponse = TypeVar("TResponse")

class UseCase(ABC, Generic[TRequest, TResponse]):
    @abstractmethod
    def execute(self, request: TRequest) -> TResponse: ...
```

هر Use Case:

- یک Command/Query DTO ورودی (`frozen dataclass`) می‌گیرد.
- یک Result DTO خروجی (`frozen dataclass`) برمی‌گرداند.
- فقط با Interfaceهای `domain` (Repository) و `application/shared/ports.py` (Service)
  کار می‌کند؛ هرگز مستقیماً به `infrastructure` وابسته نیست (تزریق از طریق constructor).
- منطق state-machine/business rule را به Entity/Domain Service واگذار می‌کند و خودش
  فقط orchestration + exception translation انجام می‌دهد.

## 2. Ports مشترک (`application/shared/ports.py`)

```python
class IPasswordHasher(ABC):
    @abstractmethod
    def hash(self, plain_password: str) -> str: ...
    @abstractmethod
    def verify(self, plain_password: str, hashed: str) -> bool: ...

class ITokenService(ABC):
    @abstractmethod
    def generate_access_token(self, user_id: EntityId, roles: list[str]) -> str: ...
    @abstractmethod
    def generate_refresh_token(self) -> tuple[str, str]: ...
        # -> (raw_token, jti)  — raw فقط یک‌بار به کاربر داده می‌شود، hash آن ذخیره می‌شود
    @abstractmethod
    def hash_refresh_token(self, raw_token: str) -> str: ...
    @abstractmethod
    def decode_access_token(self, token: str) -> "AccessTokenPayload": ...
        # raise InvalidTokenError / ExpiredTokenError

@dataclass(frozen=True)
class AccessTokenPayload:
    user_id: EntityId
    roles: list[str]
    expires_at: datetime

class IClock(ABC):
    @abstractmethod
    def now(self) -> datetime: ...

class IIdGenerator(ABC):
    @abstractmethod
    def new_id(self) -> EntityId: ...

class IUnitOfWork(ABC):
    """کنترل تراکنش برای Use Caseهایی که چند Aggregate/Repository را با هم تغییر می‌دهند."""
    @abstractmethod
    def __enter__(self) -> "IUnitOfWork": ...
    @abstractmethod
    def __exit__(self, exc_type, exc, tb) -> None: ...
    @abstractmethod
    def commit(self) -> None: ...
    @abstractmethod
    def rollback(self) -> None: ...

class IEventPublisher(ABC):   # از domain.shared.events بازتعریف/re-export می‌شود
    @abstractmethod
    def publish(self, events: list["DomainEvent"]) -> None: ...

class INotificationService(ABC):
    @abstractmethod
    def send_email(self, to: str, subject: str, body: str) -> None: ...
    @abstractmethod
    def send_verification_email(self, to: str, token: str) -> None: ...
    @abstractmethod
    def send_password_reset_email(self, to: str, token: str) -> None: ...

class IFileStorageService(ABC):
    @abstractmethod
    def get_metadata(self, file_asset_id: EntityId) -> "FileAssetMetadata": ...
    @abstractmethod
    def register_uploaded_file(self, ...) -> EntityId: ...
```

```python
# application/shared/authorization.py
class IAuthorizationService(ABC):
    @abstractmethod
    def has_permission(self, user_id: EntityId, permission_key: str) -> bool: ...
    @abstractmethod
    def require_permission(self, user_id: EntityId, permission_key: str) -> None: ...
        # raise PermissionDeniedError
    @abstractmethod
    def has_role(self, user_id: EntityId, role_key: str) -> bool: ...
```

این Interface اجازه می‌دهد قانون «فقط Admin می‌تواند X را انجام دهد» به‌صورت یک‌خطی در
هر Use Case چک شود بدون آنکه منطق RBAC در همه‌جا کپی شود. پیاده‌سازی واقعی‌اش (join روی
`user_roles`/`role_permissions`) در `infrastructure` فاز ۲ می‌آید؛ در فاز ۱ فقط
Interface + یک Fake ساده برای تست لازم است.

## 3. سازمان‌دهی هر context در application

```
application/<context>/
├── dto.py            # Command/Query + Result dataclassها
├── exceptions.py      # Application-level exceptions (بخش‌هایی که Domain error نیستند)
└── use_cases/
    └── <use_case_name>.py   # هر Use Case در فایل خودش، یک کلاس
```

---

## 4. IAM — Use Caseها (فاز ۱، Core)

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

    def execute(self, request: RegisterUserCommand) -> RegisterUserResult:
        # 1. Email(request.email) -> ValueError پس از validate -> map به DuplicateEmailError اگر تکراری
        # 2. اگر user_repo.exists_by_email(...) -> raise DuplicateEmailError
        # 3. hash password با password_hasher
        # 4. new User(status=PENDING) + role پیش‌فرض customer
        # 5. با uow: user_repo.add(user); user_role_repo.add(default_role); uow.commit()
        # 6. notification_service.send_verification_email(...)
        # 7. return RegisterUserResult(...)
        ...
```

خطاهای قابل انتظار: `DuplicateEmailError` (از domain) → در `presentation` (فاز۲) به HTTP 409
نگاشت می‌شود طبق `ERROR_HANDLING.md`.

### LoginUser

ورودی: email/password. جریان: `user_repo.get_by_email` → اگر نبود `InvalidCredentialsError`
(نه `UserNotFoundError`، تا email enumeration جلوگیری شود) → `password_hasher.verify` →
اگر user.status != ACTIVE → `UserNotActiveError` → تولید access/refresh token →
`refresh_token_repo.add(...)` → `user_repo.update` (record_login).

### LogoutUser

ورودی: `refresh_token_jti`. جریان: پیدا کردن توکن → `revoke()` → `update`.

### RefreshToken

ورودی: `raw_refresh_token`. جریان: hash کردن raw token → پیدا کردن با hash →
`is_valid(now)` چک شود وگرنه `InvalidRefreshTokenError` → صدور access token جدید →
(اختیاری) rotation: صدور refresh token جدید و revoke قبلی با `replaced_by_token_id`.

### ChangePassword / ForgotPassword

`ChangePasswordUseCase(user_id, old_password, new_password)`:
verify رمز قدیم → hash جدید → `user.change_password(...)` → `update`.
`ForgotPasswordUseCase(email)`: برای جلوگیری از User-enumeration، فقط اگر
`exists_by_email(email)` باشد توکن یک‌بارمصرف تولید و ایمیل ارسال می‌شود؛ در هر دو حالت نتیجه
موفقیت یکسان برگردانده می‌شود.

### BlockUser / ActivateUser

نیازمند `authorization_service.require_permission(actor_id, "user.block")`.
جریان ساده: `get_by_id` → `user.block(...)`/`activate()` → `update`.

### AssignRole / RemoveRole

`AssignRoleUseCase(actor_id, target_user_id, role_key)`:
require_permission("user.assign_role") → role = `role_repo.get_by_key` →
اگر `user_role_repo.find_active` موجود بود → `RoleAlreadyAssignedError` →
`UserRole` جدید → `add`.
`RemoveRoleUseCase`: require_permission("user.remove_role") → role = `get_by_key` →
اگر `role.is_system` → `SystemRoleImmutableError` → کاربری نقش فعال نداشت →
`UserRoleNotFoundError`.

### GrantPermission / RevokePermission

`GrantPermissionUseCase`: require_permission("user.grant_permission") →
role = `role_repo.get_by_id` و permission = `permission_repo.get_by_id` →
اگر permission قبلاً به نقش داده شده (`list_permissions_for_role`) →
`PermissionAlreadyGrantedError` → `RolePermission` جدید → `add`.
`RevokePermissionUseCase`: require_permission("user.revoke_permission") →
role = `role_repo.get_by_id`؛ اگر `role.is_system` → `SystemRoleImmutableError` →
`permission_repo.get_by_id` چک وجود → `role_permission_repo.remove`.

---

## 5. Freelancer — Use Caseها (فاز ۱)

- `CreateFreelancerProfileUseCase(user_id, display_name, ...)` → چک عدم وجود پروفایل قبلی
  → `FreelancerProfile(approval_status=PENDING)` → `add`.
- `UpdateFreelancerProfileUseCase` → `get_by_user_id` → فیلدهای مجاز (`bio`, `skills`
  اگر باشد, `city`, `hourly_rate_*` از طریق `update_rate_range`) → `update`.
- `UploadResumeUseCase(profile_id, file_asset_id, summary)` → `file_storage.get_metadata`
  برای اطمینان از وجود فایل → نسخه جدید `Resume(version_no=last+1, is_current=True)` →
  نسخه قبلی `mark_as_current(False)` (یا معادل) → `add`/`update`.
- `AddPortfolioItemUseCase` / `UpdatePortfolioItemUseCase` / `DeletePortfolioItemUseCase`.
- `SubmitFreelancerApprovalUseCase(profile_id)` → `profile.submit_for_approval()` → `update`.
- `ApproveFreelancerUseCase(actor_id, profile_id, note)` → require_permission
  ("freelancer.approve") → `profile.approve(actor_id, now, note)` → `update` +
  `FreelancerLevelHistory` اولیه اگر level پیش‌فرض تنظیم شود.
- `RejectFreelancerUseCase(actor_id, profile_id, note)`.
- `AssignFreelancerLevelUseCase(actor_id, profile_id, new_level_id, reason)` →
  `level_repo.get_by_id` (چک وجود) → `profile.change_level(...)` →
  `FreelancerLevelHistory` رکورد شود → `update`.
- `GetFreelancerProfileUseCase(profile_id)` — Query ساده، فقط خواندن.
- `GetFreelancerStatisticsUseCase(profile_id)` → از `IRatingRepository` و
  `IProjectApplicationRepository`/`IProjectRepository` آمار می‌گیرد (aggregation ساده در
  Use Case چون Cross-Repository است).

  > **تغییر نسبت به برنامه اولیه:** در فاز ۹، این Use Case به صورت
  > `GetFreelancerStatisticsUseCase` در context گزارش‌گیری پیاده شد و آمار را از
  > `IReportingReadRepository` می‌گیرد (نه aggregation مستقیم).

---

## 6. Category — Use Caseها (فاز ۱)

- `CreateCategoryUseCase` / `UpdateCategoryUseCase` / `DeleteCategoryUseCase` (soft delete).
- `AssignSupervisorUseCase(actor_id, category_id, supervisor_user_id)` →
  require_permission("category.assign_supervisor") → چک تکراری‌نبودن →
  `CategorySupervisor` جدید → `add`.
- `RemoveSupervisorUseCase`.
- `GetCategoriesUseCase` / `GetCategoryProjectsUseCase` (این یکی از `IProjectRepository`
  هم استفاده می‌کند).

  > **تغییر نسبت به برنامه اولیه:** `GetCategoryProjects` در فاز ۵ (بعد از ایجاد
  > `IProjectRepository`) پیاده شد، نه در فاز ۲.

---

## 7. Dynamic Form Engine — Use Caseها (فاز ۱)

- `CreateFormTemplateUseCase(category_id, name, template_key)` → نسخه اول
  `FormTemplate(version_no=1, status=DRAFT)`.
- `UpdateFormTemplateUseCase` (فقط اگر DRAFT).
- `PublishFormTemplateUseCase(template_id, published_by)` →
  `template.publish(...)` (خطا اگر field نداشته باشد) → `update`.
- `AddFieldUseCase` / `UpdateFieldUseCase` / `RemoveFieldUseCase`.
- `AddFieldOptionUseCase` (فقط برای select/multi_select — خطای domain
  `InvalidFieldOptionError` اگر نوع فیلد اشتباه باشد).
- `GetFormTemplateUseCase(category_id)` → `get_published_for_category`.

---

## 8. Project Management — Use Caseها (فاز ۱، مهم‌ترین بخش)

### CreateProject

```python
@dataclass(frozen=True)
class CreateProjectCommand:
    actor_id: EntityId            # احراز هویت
    customer_user_id: EntityId
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
    # وابستگی‌ها: IProjectRepository, ICategoryRepository, IFormTemplateRepository,
    #             IIdGenerator, IClock, IUnitOfWork
    def execute(self, request: CreateProjectCommand) -> ProjectResult:
        # 1. category = category_repo.get_by_id (raise CategoryNotFoundError)
        # 2. form_template = form_template_repo.get_published_for_category(category.id)
        # 3. validate form_values بر اساس form_template.fields (is_required, field_type)
        #    -> در صورت خطا: FormValidationError (application-level)
        # 4. project_code تولید شود (Domain Service یا application util)
        # 5. Project جدید با status=DRAFT ساخته شود
        # 6. project_repo.add(project) + project_form_value ذخیره (خارج از دامنه Project
        #    اگر آن را Aggregate جدا در نظر بگیریم؛ یا به‌عنوان بخشی از همان تراکنش)
        ...
```

### PublishProject

`project.publish(now)` → `start_collecting_applications()` بلافاصله یا در یک مرحله جدا
طبق state diagram مستند سوم؛ توصیه: `publish()` مستقیماً به `COLLECTING_APPLICATIONS`
برود چون در مستندات «Published» و «Collecting Applications» عملاً پشت‌سرهم‌اند —
این تصمیم باید در Entity مستند شود (docstring) که چرا دو enum جدا نگه داشته شده (تاریخچه
دقیق state) ولی transition پشت‌سرهم انجام می‌شود.

### CancelProject

`authorize_owned_action(authz, actor_id, project.customer_user_id,
"project.manage_own", "project.manage_any")` → `project.cancel(now, reason)` →
`project_status_history_repo.add(...)`.

### ApplyForProject

وابستگی‌ها: `IProjectRepository`, `IProjectApplicationRepository`,
`IFreelancerProfileRepository`, `IFreelancerLevelRepository`, `IAuthorizationService`,
`IUnitOfWork`.
جریان:

0. `authorization_service.require_permission(actor_id, "project.apply")`.
1. `project = project_repo.get_by_id` → چک `project.can_accept_applications()`.
2. چک `project.is_application_deadline_passed(now)` → `ApplicationDeadlineExpiredError`.
3. `profile = freelancer_profile_repo.get_by_user_id(actor_id)` → چک `is_approved()`
   وگرنه `FreelancerNotApprovedError`.
4. چک تکراری با `find_by_project_and_freelancer` → `DuplicateApplicationError`.
5. `level = level_repo.get_by_id(profile.current_level_id)`.
6. `active_count = application_repo.count_active_for_freelancer(profile.id)`.
7. `FreelancerEligibilityPolicy.is_eligible_to_apply(level, project, active_count)`
   وگرنه `FreelancerNotEligibleError`.
8. `ProjectApplication` جدید (status=APPLIED) با `submitted_by_user_id=actor_id` → `add`.

### WithdrawApplication / ViewApplications

### AcceptFreelancer

تراکنش چند-Aggregateای؛ حتماً با `IUnitOfWork`:

1. `application = application_repo.get_by_id`.
2. `project = project_repo.get_by_id(application.project_id)`.
3. احراز هویت بر اساس قرارداد مالکیت دو-سطحی (see AUTHORIZATION.md §3.1):
   `authorize_owned_action(authz, actor_id, project.customer_user_id,
   "project.manage_own", "project.manage_any")` — اگر actor خودِ customer باشد
   `project.manage_own` وگرنه (admin) `project.manage_any` لازم است؛ وگرنه
   `PermissionDeniedError`.
4. `application.accept(actor_id, now)`.
5. `project.assign_freelancer(application.id, now)`.
6. سایر application‌های `list_by_project` که `APPLIED/SHORTLISTED` هستند → `reject(...)`.
7. `project_status_history_repo.add(...)`.
8. `uow.commit()`.

### RejectFreelancer / StartProject

### SubmitDelivery

وابستگی‌ها شامل `IProjectDeliveryRepository`. چک: actor باید همان freelancer منتخب
پروژه باشد (`project.selected_application_id` → application → `freelancer_profile.user_id
== actor_id`). `version_no = last + 1`. اگر delivery قبلی وجود دارد و در `REVISION_REQUESTED`
بود → delivery قبلی `supersede(new.id)`. سپس:
`project.mark_delivery_submitted()` → اگر `project.has_supervisor()`:
`project.move_to_supervisor_review()` وگرنه `project.move_to_customer_review()`.

### RequestRevision

وابستگی‌ها: `IProjectRevisionRequestRepository` + `RevisionPolicy`.

1. `count = revision_repo.count_by_project(project_id)`.
2. اگر `not RevisionPolicy.can_request_new_revision(...)` → `MaxRevisionsExceededError`.
3. `ProjectRevisionRequest(round_no=count+1, status=OPEN)` → `add`.
4. `project.request_revision()` → `update`.

### ApproveDelivery / RejectDelivery (سطح Project — تکمیل جریان)

این‌ها با Use Caseهای context `review` هماهنگ کار می‌کنند (بخش ۹) — منطق تغییر Project
status اینجا انجام می‌شود، تصمیم تایید/رد در `review` context ثبت می‌شود.

### CompleteProject

چک: `project.status == AWAITING_CUSTOMER_REVIEW` و actor == customer →
`project.complete(now)` → `update`.

### GetProjectDetails / GetMyProjects / GetAvailableProjects

Queryهای خواندن؛ `GetAvailableProjects` از `list_available_for_freelancer` استفاده
می‌کند که سطح دسترسی فریلنسر را هم چک می‌کند (فیلتر در Repository interface تعریف شده،
پیاده‌سازی واقعی در infra).

---

## 9. Quality Assurance / Supervisor Review — Use Caseها (فاز ۱)

- `GetSupervisorProjectsUseCase(supervisor_user_id)` → `project_repo.list_by_supervisor`.
- `GetPendingReviewsUseCase(supervisor_user_id)` → `supervisor_review_repo
.list_pending_for_supervisor`.
- `ReviewDeliveryUseCase` / `ApproveDeliveryUseCase` / `RejectDeliveryUseCase`
  (هر سه از Domain Service مشترک `decide_delivery_review` در `review/use_cases/review_workflow.py`
  استفاده می‌کنند):
  1. `delivery = delivery_repo.get_by_id`.
  2. `project = project_repo.get_by_id(delivery.project_id)`.
  3. پیش‌شرط وضعیت: `project.status` باید `UNDER_SUPERVISOR_REVIEW` باشد وگرنه
     `InvalidStateTransitionError`.
  4. احراز هویت دو-سطحی: اگر `category_supervisor_repo.is_supervisor_of(actor_id,
     project.category_id)` → `require_permission(actor_id, "review.decide_own")` وگرنه
     `require_permission(actor_id, "review.decide_any")` (admin) → `PermissionDeniedError`.
  5. `SupervisorReview` جدید یا موجود؛ اگر تصمیم‌گرفته‌شده باشد → `DeliveryAlreadyReviewedError`.
  6. `review.approve(...)`/`review.reject(reason)` → `add` (جدید) یا `update` (موجود).
  7. `delivery.approve(...)`/`reject(...)` → `update`.
  8. Project: approve → `move_to_customer_review()`؛ reject → ساخت `ProjectRevisionRequest`
     (قبل از آن `RevisionPolicy.ensure_can_request_new_revision` → `MaxRevisionsExceededError`)
     و `request_revision()`.

---

## 10. Feedback & Rating — Use Caseها (فاز ۱)

- `SubmitReviewUseCase(actor_id, project_id, decision, comment)`:
  احراز هویت: `authorize_owned_action(authz, actor_id, project.customer_user_id,
  "feedback.manage_own", "feedback.manage_any")`. چک
  `project.status == AWAITING_CUSTOMER_REVIEW` →
  `CustomerReview` → `add`. اگر decision == APPROVED → `Project.complete`؛ اگر REJECTED →
  ساخت `ProjectRevisionRequest` (قبل از آن `RevisionPolicy.ensure_can_request_new_revision`)
  و `request_revision()`.
- `SubmitRatingUseCase(actor_id, project_id, score, comment, is_public)`:
  1. `project = project_repo.get_by_id`.
  2. احراز هویت: `authorize_owned_action(..., "feedback.manage_own", "feedback.manage_any")`.
  3. اگر `project.status != COMPLETED` → `ProjectNotCompletedError`.
  4. اگر `rating_repo.find_by_project` موجود → `RatingAlreadyExistsError`.
  5. `Rating(score=...)` (validate در `__post_init__` دامنه) → `add`.
- `GetFreelancerRatingsUseCase` / `GetProjectRatingUseCase`.

---

## 11. Communication / Ticketing — Use Caseها (فاز ۱)

- `CreateTicketUseCase(actor_id, subject, related_project_id, priority)` →
  `Ticket(status=OPEN)` + `TicketParticipant(role=REQUESTER)` → `add`.
- `AssignTicketUseCase(actor_id, ticket_id, assignee_user_id)` →
  `require_permission(actor_id, "ticket.assign")`.
- `SendMessageUseCase(actor_id, ticket_id, body, attachments)` →
  چک `ticket.is_closed()` → `TicketClosedError` وگرنه پیام ثبت + `touch_last_message`.
- `GetTicketMessagesUseCase` / `GetUserTicketsUseCase` — latter: `authorize_owned_action(authz,
  actor_id, user_id, "ticket.read_own", "ticket.read_any")`; CloseTicket:
  `authorize_owned_action(authz, actor_id, ticket.created_by_user_id, "ticket.close_own",
  "ticket.close_any")` + چک participant.
- `CloseTicketUseCase(actor_id, ticket_id)` → `ticket.close(actor_id, now)`.

---

## 12. Reporting & Analytics — Use Caseها (فاز ۱، Read-Only)

- `GetDashboardStatisticsUseCase()` → `reporting_read_repo.get_dashboard_statistics()`.
- `GetUserStatisticsUseCase()`, `GetProjectStatisticsUseCase()`,
  `GetFreelancerStatisticsUseCase()`, `GetCustomerStatisticsUseCase()`,
  `GetSystemAnalyticsUseCase()`.
  همه این‌ها فقط `require_permission("reporting.read")` چک می‌کنند و مستقیم Query را
  delegate می‌کنند؛ هیچ منطق نوشتنی ندارند.

---

## 13. Application-level Exceptions (`application/shared/exceptions.py`)

این‌ها جدا از Domain Exceptionها هستند چون به orchestration/authorization مربوط‌اند نه
به قانون ذاتی Entity (جزئیات کامل در `ERROR_HANDLING.md`):

```python
class ApplicationError(Exception): ...
class PermissionDeniedError(ApplicationError): ...
class ValidationError(ApplicationError): ...
class FormValidationError(ValidationError): ...
class ExternalServiceError(ApplicationError): ...   # وقتی یک Port بیرونی fail می‌کند
```

## 14. Wiring/Composition (یادداشت برای فاز ۲، فقط مرجع)

در فاز ۲، یک Composition Root (مثلاً `presentation/container.py`) تمام Portها را با
پیاده‌سازی واقعی `infrastructure` پر می‌کند و به Use Caseها inject می‌کند. در فاز ۱،
تست‌ها این نقش را با Fake Repository/Service ایفا می‌کنند (نگاه کن `TESTING.md`).
