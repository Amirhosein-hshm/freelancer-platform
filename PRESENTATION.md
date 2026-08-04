# PRESENTATION.md — Presentation Layer Specification (FastAPI)

Prerequisites: `API_DESIGN.md` (response format), `ERROR_HANDLING.md` (error mapping),
`AUTHORIZATION.md` (permission keys), `APPLICATION.md` (Use Cases/DTOs).

## 1. Architectural Principle

The Presentation layer is responsible only for **translating HTTP ↔ Use Case**. No business logic belongs here. Every endpoint: (1) authenticates the user from the JWT, (2) converts the Request Schema into a Command/Query DTO, (3) invokes the Use Case through `execute()`, and (4) wraps the Result DTO inside a `SuccessEnvelope`. Endpoints do not catch exceptions themselves—a global Exception Handler is responsible for that.

## 2. Directory Structure

**Important architectural note:** `presentation` must never import directly from `infrastructure`—doing so violates the dependency rule of Clean Architecture (`presentation` is an inner layer relative to `infrastructure`; dependencies are only allowed to point inward). The actual wiring (which concrete Repository implements which Interface) is performed in a separate outer package named `bootstrap/`, equivalent to the **"Main Component"** concept described in the Clean Architecture book. Full details are provided in §3.

```text
src/app/presentation/
├── main.py                       # create_app() -> FastAPI instance; only includes
│                                  # routers and registers error handlers—
│                                  # no concrete implementations are created here
├── core/
│   ├── envelope.py                # SuccessEnvelope, ErrorEnvelope, PaginationMeta
│   ├── error_handlers.py          # exception_handler for each base class defined in ERROR_HANDLING.md
│   ├── security.py                # get_current_user (uses providers.get_token_service)
│   ├── providers.py               # provider stubs: abstract signatures for each Port/Use Case,
│   │                               # without importing anything from infrastructure
│   │                               # (function bodies only raise NotImplementedError;
│   │                               # bootstrap overrides them)
│   └── pagination.py              # PageQuery dependency (page, page_size)
│
├── websocket/
│   ├── connection_manager.py      # in-memory map: user_id -> set[WebSocket]
│   └── router.py                  # WebSocket endpoint: /ws/notifications
│
└── api/v1/
    ├── auth/
    │   ├── router.py              # /auth/register /auth/login /auth/refresh /auth/logout /auth/me
    │   └── schemas.py
    ├── iam/            (admin user & role management)
    │   ├── router.py
    │   └── schemas.py
    ├── freelancer/
    ├── category/
    ├── form/
    ├── project/
    ├── review/
    ├── feedback/
    ├── ticketing/
    └── reporting/
```

Each context contains a `router.py` (endpoints) and a `schemas.py` (Pydantic Request/Response models). An optional `dependencies.py` may be added if that context requires custom dependencies (which should be rare).

## 3. Composition Root — Why It Lives Outside `presentation`

`presentation/core/providers.py` defines only the **dependency signatures**, without any concrete implementation:

```python
# presentation/core/providers.py  (no imports from app.infrastructure)
def get_project_repository() -> IProjectRepository:
    raise NotImplementedError("must be overridden by bootstrap.container")

def get_token_service() -> ITokenService:
    raise NotImplementedError("must be overridden by bootstrap.container")

def get_create_project_use_case(
    authz: IAuthorizationService = Depends(get_authorization_service),
    project_repo: IProjectRepository = Depends(get_project_repository),
    category_repo: ICategoryRepository = Depends(get_category_repository),
    ...
) -> CreateProjectUseCase:
    return CreateProjectUseCase(authz, project_repo, category_repo, ...)
```

Each router depends only on `Depends(get_<use_case>_use_case)` from `providers.py`. That provider function is itself composed only from other provider stubs (not concrete classes), so nowhere inside `presentation` does the code know about `SqlAlchemyProjectRepository`, `JwtTokenService`, or any other concrete implementation.

The actual wiring is performed in a separate outer package named **`src/app/bootstrap/`**—the only place in the entire project that is allowed to import both `presentation` and `infrastructure` (equivalent to the **"Main Component"** concept in the Clean Architecture book: a component outside all four layers whose sole responsibility is connecting concrete implementations to abstractions):

```python
# bootstrap/container.py
from app.presentation.core import providers
from app.presentation.main import create_app
from app.infrastructure.repositories.project_repository import SqlAlchemyProjectRepository
from app.infrastructure.security.token_service import JwtTokenService
# ...

def build_app() -> FastAPI:
    app = create_app()
    app.dependency_overrides[providers.get_project_repository] = (
        lambda session=Depends(get_db_session): SqlAlchemyProjectRepository(session)
    )
    app.dependency_overrides[providers.get_token_service] = (
        lambda: JwtTokenService(secret=settings.jwt_secret, ...)
    )
    # ... one override for each provider stub
    return app
```

```python
# bootstrap/run.py — the actual uvicorn entry point
from app.bootstrap.container import build_app

app = build_app()
```

FastAPI's `app.dependency_overrides` is designed precisely for this purpose. Its primary documented use case is testing, meaning the exact same mechanism is reused in `PRESENTATION.md §... (Testing)` with fake implementations, without introducing a separate pattern.

`Dockerfile` and `docker-compose.yml` should start the application using `uvicorn app.bootstrap.run:app`, not `app.presentation.main:app`.

## 4. Endpoint Pattern (Complete Example)

```python
# api/v1/project/router.py
router = APIRouter(prefix="/projects", tags=["Project"])

@router.post(
    "",
    response_model=SuccessEnvelope[ProjectResponse],
    status_code=201,
    operation_id="create_project",
    responses={404: {"model": ErrorEnvelope}, 422: {"model": ErrorEnvelope}},
)
def create_project(
    payload: CreateProjectRequest,
    current_user: AccessTokenPayload = Depends(get_current_user),
    use_case: CreateProjectUseCase = Depends(get_create_project_use_case),
) -> SuccessEnvelope[ProjectResponse]:
    command = CreateProjectCommand(
        actor_id=current_user.user_id,
        customer_user_id=payload.customer_user_id or current_user.user_id,
        category_id=payload.category_id,
        title=payload.title,
        ...
    )
    result = use_case.execute(command)
    return SuccessEnvelope(message="Project created.", data=ProjectResponse.from_result(result))
```

Notes:

- `payload.customer_user_id` is optional and is used only for the _on-behalf_ workflow. If it is omitted, `actor_id` is used instead (the default self-service behavior).
- `ProjectResponse.from_result(result)` is a simple class method that converts the Result DTO into the Pydantic response model, providing explicit separation between layers.
- There is no `try/except` block inside the endpoint. If the Use Case raises an exception, it propagates to the global Exception Handler.

## 5. Authentication (`core/security.py`)

```python
security_scheme = HTTPBearer()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security_scheme),
    token_service: ITokenService = Depends(get_token_service),
) -> AccessTokenPayload:
    try:
        return token_service.decode_access_token(credentials.credentials)
    except (InvalidTokenError, ExpiredTokenError) as exc:
        raise HTTPException(status_code=401, detail="Invalid or expired token") from exc
```

Important note: `require_permission` is **not** reimplemented in the Presentation layer. That logic belongs to `IAuthorizationService` in the Application layer. Each Use Case is responsible for invoking `require_permission`; the Presentation layer only extracts the raw identity (`actor_id`) and passes it along.

This means there is no need for a separate `Depends(require_permission("project.create"))` in the router, eliminating duplicated authorization logic.

## 6. Global Exception Handling (`core/error_handlers.py`)

```python
def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(EntityNotFoundError, lambda r, e: _envelope(e, 404))
    app.add_exception_handler(InvalidStateTransitionError, lambda r, e: _envelope(e, 409))
    app.add_exception_handler(BusinessRuleViolationError, lambda r, e: _envelope(e, 422))
    app.add_exception_handler(UniqueConstraintViolationError, lambda r, e: _envelope(e, 409))
    app.add_exception_handler(PermissionDeniedError, lambda r, e: _envelope(e, 403))
    app.add_exception_handler(ValidationError, lambda r, e: _envelope(e, 400))
    app.add_exception_handler(ExternalServiceError, lambda r, e: _envelope(e, 502))
    app.add_exception_handler(Exception, _unhandled)  # 500 + log, generic message

def _envelope(exc: Exception, status: int) -> JSONResponse:
    code = re.sub(r"(?<!^)(?=[A-Z])", "_", type(exc).__name__.removesuffix("Error")).upper()
    return JSONResponse(status_code=status, content=ErrorEnvelope(
        error=ErrorDetail(code=code, message=str(exc))
    ).model_dump())
```

These seven registrations are fixed. There is never any need to write additional code for every concrete Exception defined throughout `DOMAIN.md` or `APPLICATION.md`, even if there are dozens of them.

## 7. WebSocket for Notifications

FastAPI provides native WebSocket support, so no additional library is required.

```python
# websocket/connection_manager.py
class ConnectionManager:
    def __init__(self) -> None:
        self._connections: dict[EntityId, set[WebSocket]] = defaultdict(set)

    async def connect(self, user_id: EntityId, ws: WebSocket) -> None:
        await ws.accept()
        self._connections[user_id].add(ws)

    def disconnect(self, user_id: EntityId, ws: WebSocket) -> None:
        self._connections[user_id].discard(ws)

    async def send_to_user(self, user_id: EntityId, payload: dict) -> None:
        for ws in list(self._connections.get(user_id, ())):
            await ws.send_json(payload)

manager = ConnectionManager()
```

```python
# websocket/router.py
@router.websocket("/ws/notifications")
async def notifications_ws(
    ws: WebSocket,
    token: str = Query(...),
    token_service: ITokenService = Depends(get_token_service),
) -> None:
    payload = token_service.decode_access_token(token)  # auth via query parameter (WS has no headers)
    await manager.connect(payload.user_id, ws)
    try:
        while True:
            await ws.receive_text()  # keep-alive; the client does not need to send anything meaningful
    except WebSocketDisconnect:
        manager.disconnect(payload.user_id, ws)
```

This singleton `ConnectionManager` forms the implementation of `INotificationService` (or at least its real-time notification component) in `infrastructure/notifications/websocket_notification_service.py` (see `INFRASTRUCTURE.md` §5).

This design works only for a single application instance because the connection state is stored in memory. If the application is later deployed with multiple instances behind a load balancer, a Redis pub/sub layer must be introduced between them.

**This will not be implemented in the current phase** (following the principle of simplicity); we merely document this limitation here.

## 8. Pagination Dependency

```python
# core/pagination.py
class PageQuery(BaseModel):
    page: int = Query(1, ge=1)
    page_size: int = Query(20, ge=1, le=100)

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size
```

## 9. Middleware

- CORS (`CORSMiddleware`) — allowed origins are read from `Settings` (environment variables).
- A lightweight request ID middleware (generating one UUID per request and returning it in the `X-Request-Id` response header) is included solely for log traceability. No business logic depends on this value.
- **No global authentication middleware.** Instead, each protected endpoint explicitly declares `Depends(get_current_user)`. Public endpoints such as `GET /categories` simply omit this dependency. This approach is much clearer than a global middleware that requires per-route exceptions.

## 10. Request Schema vs. Command DTO — Why We Have Two Models

`CreateProjectRequest` (a Pydantic model in the Presentation layer) does **not** contain fields such as `actor_id`, because that information comes from the `Authorization` header rather than the HTTP request body.

In contrast, `CreateProjectCommand` (in the Application layer) includes `actor_id`, because the Use Case must remain independent of HTTP and fully testable.

This thin mapping layer is not unnecessary duplication—it is an explicit separation of concerns. If the Presentation layer changes in the future (for example, by introducing GraphQL), the Application layer remains completely unchanged.
