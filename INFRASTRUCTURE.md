# INFRASTRUCTURE.md — Infrastructure Layer Specifications

**Prerequisites:** `DOMAIN.md` (Repository Interfaces), `APPLICATION.md` (Ports), `AUTHORIZATION.md`, `PRESENTATION.md` (what is consumed from here).

---

## 1. Architectural Principle

Every file in this layer implements an interface from the domain/application layer — no new business logic is written here, only data transformation (`ORM row ↔ domain Entity`) and external library calls (DB, JWT, hashing).

---

## 2. Directory Structure

```text
src/app/infrastructure/
├── config.py                       # Settings (pydantic-settings), read from env
├── db/
│   ├── base.py                      # SQLAlchemy declarative base, naming convention
│   ├── session.py                   # async engine + session factory, get_db_session dependency
│   ├── unit_of_work.py              # SqlAlchemyUnitOfWork(IUnitOfWork)
│   └── models/                      # One model file per domain area (not necessarily per entity)
│       ├── iam_models.py             # UserModel, RoleModel, PermissionModel, ...
│       ├── freelancer_models.py
│       ├── category_models.py
│       ├── form_models.py
│       ├── project_models.py
│       ├── review_models.py
│       ├── feedback_models.py
│       ├── ticketing_models.py
│       └── sequence_models.py        # CodeSequenceModel (for project/ticket code generator)
│
├── repositories/                    # One file per Repository Interface
│   ├── user_repository.py            # SqlAlchemyUserRepository(IUserRepository)
│   ├── project_repository.py
│   └── ...
│
├── security/
│   ├── password_hasher.py            # Argon2PasswordHasher(IPasswordHasher)
│   ├── token_service.py              # JwtTokenService(ITokenService)
│   └── authorization_service.py      # SqlAlchemyAuthorizationService(IAuthorizationService)
│
├── notifications/
│   └── websocket_notification_service.py  # WebSocketNotificationService(INotificationService)
│
├── clock.py                         # SystemClock(IClock)
├── id_generator.py                  # UuidIdGenerator(IIdGenerator)
├── code_generators.py                # SqlSequenceProjectCodeGenerator, ...ITicketCodeGenerator
│
├── migrations/                       # Alembic
│   ├── env.py
│   └── versions/
│
└── seed/
    ├── seed_data.py                  # Static list of roles/permissions/role_permissions (Python, not raw SQL)
    └── run_seed.py                   # Idempotent script, called from docker entrypoint

```

---

## 3. Database (SQLAlchemy 2.0 async + PostgreSQL)

- **Engine:** `create_async_engine` with the `asyncpg` driver.
- Each SQLAlchemy model in `db/models/` is defined independently of the domain Entity (two separate classes: `UserModel` ORM and `User` domain Entity) — explicit transformation is performed in the Repository (`_to_domain(row) -> User`, `_to_model(entity) -> UserModel`). This separation is intentional: the domain never depends on SQLAlchemy (following the dependency direction rule in `ARCHITECTURE.md`).
- Migrations with Alembic, separate from seed data (Section 7).
- Explicit naming conventions for constraints (`ix_`, `uq_`, `fk_`, ...) in `db/base.py` to make automated migrations predictable.

### Example Repository

```python
# repositories/project_repository.py
class SqlAlchemyProjectRepository(IProjectRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, project: Project) -> None:
        self._session.add(_to_model(project))

    async def get_by_id(self, project_id: EntityId) -> Project:
        row = await self._session.get(ProjectModel, project_id)
        if row is None:
            raise ProjectNotFoundError(f"Project {project_id} not found.")
        return _to_domain(row)

    async def list_by_customer(
        self, customer_user_id: EntityId, status: ProjectStatus | None, limit: int, offset: int
    ) -> tuple[list[Project], int]:
        ...  # Real SELECT with LIMIT/OFFSET + a separate COUNT(*) query for total

```

**Important Async Note:** Because FastAPI and SQLAlchemy are async, but Phase 1 Use Cases were written as synchronous (`def execute`), we have two options:

1. **Make Use Cases async (`async def execute`):** Changes in `application/shared/use_case.py` and all signatures.
2. **Keep Repository implementations sync** with a sync driver (like `psycopg2`/`psycopg3` sync mode) and have FastAPI call them using `run_in_threadpool`.

**Recommended decision for this project (simplicity prioritized): Option 1 — Make Use Cases async.**
This change must be done as a separate step at the very beginning of the infrastructure work (converting all `def execute` to `async def execute` and awaiting repository/service calls), because otherwise async SQLAlchemy sessions will not function properly without an active event loop. We state this explicitly in the prompts.

---

## 4. Unit of Work

```python
class SqlAlchemyUnitOfWork(IUnitOfWork):
    def __init__(self, session_factory: async_sessionmaker) -> None:
        self._session_factory = session_factory

    async def __aenter__(self) -> "SqlAlchemyUnitOfWork":
        self.session = self._session_factory()
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        if exc_type is not None:
            await self.session.rollback()
        await self.session.close()

    async def commit(self) -> None:
        await self.session.commit()

    async def rollback(self) -> None:
        await self.session.rollback()

```

**Note:** Each Repository must receive the session corresponding to the current request's UoW — this is guaranteed via FastAPI per-request session dependency injection (`get_db_session` creates a fresh session per HTTP request; all Repositories for that request receive the same session via `Depends`).

---

## 5. Security Implementations

- **`Argon2PasswordHasher(IPasswordHasher)`:** Using `argon2-cffi`, the library's default parameters (`time_cost`/`memory_cost`) are sufficient; over-tuning is not needed in Phase 1.
- **`JwtTokenService(ITokenService)`:** Using `PyJWT` with the `HS256` algorithm (sufficient for a single service; if scaled to multiple services later, `RS256` with public/private keys). Claims: `sub` (`user_id`), `roles`, `exp`, `iat`. **Refresh token:** a cryptographically secure random string (`secrets.token_urlsafe(32)`) whose hash alone (`hashlib.sha256`) is stored in the DB — JWT itself is not used for refresh tokens because it does not require decoding; it only needs to be unguessable and revocable.
- **`SqlAlchemyAuthorizationService(IAuthorizationService)`:** Per the explicit contract in `AUTHORIZATION.md §5`: executes an actual query across the chain `user_roles → role_permissions → permissions` (via a single join), without any hardcoded shortcuts for any role, including `admin`.
- Results are not cached per request in Phase 1 (keeping it simple); if performance becomes an issue, a request-level cache can be added in a future phase.

---

## 6. Notification (WebSocket)

`WebSocketNotificationService(INotificationService)` implements the `send_email`/`send_verification_email`/`send_password_reset_email` methods as no-ops with warning logs for Phase 1 (since actual SMTP is out of scope for this phase — following the KISS principle).

For real-time notifications (e.g., "your request was approved"), a new method is added to the Port:

```python
# application/shared/ports.py — To be added
class IRealtimeNotifier(ABC):
    @abstractmethod
    async def notify_user(self, user_id: EntityId, event_type: str, payload: dict) -> None: ...

```

Its implementation calls `presentation/websocket/connection_manager.py` directly (the only place where infrastructure is permitted to import from presentation — since WebSocket connection state is inherently tied to the HTTP/transport layer; we explicitly document this in `ARCHITECTURE.md` as an exception, not an arbitrary violation of the dependency rule).

---

## 7. Seed Data (Roles / Permissions / Admin) — `seed/`

```python
# seed/seed_data.py — Static data, version-controlled in Git
ROLES = [
    {"role_key": "admin", "name": "Administrator", "is_system": True},
    {"role_key": "customer", "name": "Customer", "is_system": True},
    {"role_key": "freelancer", "name": "Freelancer", "is_system": True},
    {"role_key": "supervisor", "name": "Supervisor", "is_system": True},
]

PERMISSIONS = [
    {"permission_key": "project.create_own", "module": "project", "action": "create_own"},
    {"permission_key": "project.create_on_behalf", "module": "project", "action": "create_on_behalf"},
    # ... all PERMISSION_* used across Use Cases (copied from AUTHORIZATION.md)
]

ROLE_PERMISSIONS = {
    "customer": ["project.create_own", "project.manage_own", "feedback.manage_own", ...],
    "freelancer": ["project.apply", ...],
    "supervisor": ["review.decide_own", ...],
    "admin": ["*"],  # Special notation: expands to all PERMISSIONS without exception during seeding
}

```

```python
# seed/run_seed.py
async def run_seed() -> None:
    async with session_factory() as session:
        for role in ROLES:
            await session.execute(
                insert(RoleModel).values(**role)
                .on_conflict_do_nothing(index_elements=["role_key"])
            )
        for perm in PERMISSIONS:
            await session.execute(
                insert(PermissionModel).values(**perm)
                .on_conflict_do_nothing(index_elements=["permission_key"])
            )
        await session.flush()
        for role_key, perm_keys in ROLE_PERMISSIONS.items():
            ...  # resolve IDs, insert role_permissions with on_conflict_do_nothing

        # Primary admin — only created if no admin user exists yet
        admin_email = settings.admin_email
        admin_password = settings.admin_password
        existing = await session.execute(select(UserModel).where(UserModel.email == admin_email))
        if existing.scalar_one_or_none() is None:
            admin_user = UserModel(
                id=str(uuid4()), email=admin_email,
                password_hash=Argon2PasswordHasher().hash(admin_password),
                first_name="System", last_name="Admin", status="ACTIVE",
            )
            session.add(admin_user)
            await session.flush()
            admin_role_id = await _get_role_id(session, "admin")
            session.add(UserRoleModel(user_id=admin_user.id, role_id=admin_role_id, is_active=True))
        await session.commit()

```

**Key Idempotency Notes (why written this way — full best practices explained in `DOCKER.md §4`):** Every insert uses `ON CONFLICT DO NOTHING`, and admin creation only occurs if `admin_email` does not already exist — meaning this script can be executed hundreds of times without errors or duplicate data. `admin_email`/`admin_password` are never hardcoded — they are always read from Settings (env vars).

---

## 8. Code Generators

`SqlSequenceProjectCodeGenerator(IProjectCodeGenerator)` uses a small table `code_sequences(year INT, prefix TEXT, last_value INT, PRIMARY KEY(year, prefix))`; `next_code(year)` executes `UPDATE ... SET last_value = last_value + 1 WHERE year=... AND prefix='PRJ' RETURNING last_value` (or `INSERT ... ON CONFLICT DO UPDATE`) — this is atomic and prevents race conditions between concurrent requests (unlike `SELECT MAX(...) + 1`, which suffers from race conditions). The same pattern applies to `ITicketCodeGenerator` using `prefix='TCK'`.

---

## 9. Config (`infrastructure/config.py`)

```python
class Settings(BaseSettings):
    database_url: str
    jwt_secret: str
    jwt_access_ttl_minutes: int = 15
    jwt_refresh_ttl_days: int = 30
    admin_email: str
    admin_password: str
    cors_origins: list[str] = ["*"]

    model_config = SettingsConfigDict(env_file=".env")

```

All sensitive values (`jwt_secret`, `admin_password`, `database_url`) are read from environment variables and are never committed to code (`.env` is listed in `.gitignore`).
