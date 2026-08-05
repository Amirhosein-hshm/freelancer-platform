# Freelance Platform API

A backend for a freelance/project marketplace, built with **FastAPI**, **SQLAlchemy**
(async), and **Postgres**. It follows a clean / hexagonal architecture split across five
packages (`domain`, `application`, `infrastructure`, `presentation`, `bootstrap`) so the
core business rules stay independent of frameworks and infrastructure.

- **FastAPI** async API with JWT auth, RBAC, and response envelopes
- **SQLAlchemy 2.0** + **asyncpg** (async ORM) with **Alembic** migrations
- **RBAC** over 4 fixed roles (`admin`, `customer`, `freelancer`, `supervisor`) resolved
  through real DB joins (`user_roles → role_permissions → permissions`)
- **Argon2** password hashing and **PyJWT** access/refresh tokens
- **Docker Compose** one-shot migrate+seed, then the app

---

## Table of Contents

1. [Architecture](#architecture)
2. [Prerequisites](#prerequisites)
3. [Quick start (Docker Compose)](#quick-start-docker-compose)
4. [Running locally (bare metal)](#running-locally-bare-metal)
5. [Configuration](#configuration)
6. [API overview](#api-overview)
7. [Testing](#testing)
8. [Project layout](#project-layout)
9. [Documentation index](#documentation-index)

---

## Architecture

| Package        | Responsibility                                                                  |
| -------------- | ------------------------------------------------------------------------------- |
| `domain`       | Entities, Value Objects, repository **interfaces**, domain services. No frameworks. |
| `application`  | Async use cases (Command/Query DTOs → Result DTOs, one `execute`), authorization.    |
| `infrastructure` | SQLAlchemy/Postgres repositories, MySQL/Alembic migrations, JWT + Argon2, seeding. |
| `presentation` | FastAPI routers, response envelopes, provider **stubs** (no `infrastructure` imports). |
| `bootstrap`    | Composition root: wires real infrastructure into the presentation stubs.         |

Dependency rule: `presentation → application → domain` and
`infrastructure → application/domain`. `presentation` never imports `infrastructure`;
only `bootstrap` talks to both.

---

## Prerequisites

- **Docker** + **Docker Compose** (recommended path)
- **Python 3.12+** (for local / bare-metal development or tests)
- Shell with `curl` (for API smoke tests)

---

## Quick start (Docker Compose)

The fastest way to get the full stack (database + migrations + seed + API) running.

### 1. Configure the environment

```bash
cp .env.example .env
# edit .env: set a real JWT_SECRET and the initial ADMIN_PASSWORD
```

### 2. Build and start

```bash
docker compose up --build
```

What happens under the hood:

1. `db` — starts `postgres:16-alpine`, waits until it is health-checked.
2. `migrate` — one-shot service running `alembic upgrade head && python -m app.infrastructure.seed.run_seed`. It creates the schema, then idempotently seeds roles/permissions and the primary admin. Exits `0` on success.
3. `app` — starts **only after** `migrate` completes successfully.

### 3. Verify it is running

- Interactive API docs: <http://localhost:8000/docs>
- Health/auth smoke test with the seeded admin:

```bash
curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"<ADMIN_PASSWORD>"}'
```

Use the returned `access_token`, then confirm the current user's roles/permissions:

```bash
TOKEN="<access_token from the previous step>"
curl -s http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer $TOKEN"
```

The response should include `roles` and `permissions` populated from the seeded admin.

> The `.env` `ADMIN_PASSWORD` is a temporary initial credential. Change it (or the
> password) after your first login.

### Stopping

```bash
docker compose down        # stop containers
docker compose down -v     # also delete the database volume (destroy all data)
```

---

## Running locally (bare metal)

If you prefer to run the services directly against a Postgres you already have:

### 1. Create a virtualenv and install

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"     # includes runtime deps + dev/test tools
```

### 2. Point the app at your Postgres

Create a `.env` (see [Configuration](#configuration)) with a `DATABASE_URL` that
targets a reachable Postgres, e.g.:

```bash
DATABASE_URL=postgresql+asyncpg://app_user:change_me@localhost:5432/freelance_platform
```

### 3. Run migrations and seed

```bash
alembic upgrade head
python -m app.infrastructure.seed.run_seed
```

### 4. Start the API

```bash
uvicorn app.bootstrap.run:app --host 0.0.0.0 --port 8000 --reload
```

Then open <http://localhost:8000/docs> and follow the smoke test above.

---

## Configuration

All configuration is read from the environment / a `.env` file (see `.env.example`).
Every variable except the JWT TTLs and CORS origins is required.

| Variable                  | Default                          | Description                                    |
| ------------------------- | -------------------------------- | ---------------------------------------------- |
| `POSTGRES_DB`             | `freelance_platform`             | Database name (used by the `db` container).    |
| `POSTGRES_USER`           | `app_user`                       | Database user (used by the `db` container).    |
| `POSTGRES_PASSWORD`       | `change_me`                      | Database password (used by the `db` container).|
| `DATABASE_URL`            | —                                | SQLAlchemy async URL incl. credentials/host.   |
| `JWT_SECRET`              | —                                | Secret for signing access tokens. Use a long random value. |
| `JWT_ACCESS_TTL_MINUTES`  | `15`                             | Access token lifetime.                         |
| `JWT_REFRESH_TTL_DAYS`    | `30`                             | Refresh token lifetime.                        |
| `ADMIN_EMAIL`             | —                                | Email of the seeded admin user.                |
| `ADMIN_PASSWORD`          | —                                | Initial password of the seeded admin.          |
| `CORS_ORIGINS`            | `["*"]`                          | Allowed CORS origins (JSON list).              |

> In Docker, `DATABASE_URL` must reference the `db` service hostname (e.g.
> `@db:5432/...`), not `localhost`.

---

## API overview

All routes are versioned under `/api/v1` and wrapped in a JSON response envelope
(`success` / `message` / `data` / `meta`). See `API_DESIGN.md` for the exact shape.

| Area                 | Prefix            | Highlights                                              |
| -------------------- | ----------------- | ------------------------------------------------------- |
| Auth                 | `/auth`           | `POST /register`, `/login`, `/refresh`, `/logout`, `GET /me` |
| IAM (admin)          | `/users`          | Admin user CRUD, role assignment, permission grants      |
| Freelancers          | `/freelancers`    | Profiles, portfolio, approvals                           |
| Categories           | `/categories`     | Category tree                                           |
| Dynamic forms        | `/forms`          | Form templates and their fields                         |
| Projects (core)      | `/projects`       | Create/publish/apply/deliver/review projects            |
| Review               | `/review`         | Supervisor reviews and deliveries                       |
| Feedback & rating    | `/feedback`       | Customer reviews and ratings                            |
| Ticketing            | `/tickets`        | Support tickets and messages                            |
| Reporting            | `/reporting`      | Read-only statistics dashboards                         |

Authentication is via `Authorization: Bearer <token>`. The JWT carries only the roles;
permissions are resolved fresh from the database on each request via `IAuthorizationService`.

---

## Testing

```bash
source .venv/bin/activate

# Unit tests (domain + application) — no external services required
pytest -q

# With coverage (target ≥ 90% on domain + application)
pytest --cov=app.domain --cov=app.application --cov-report=term-missing \
  --cov-fail-under=90

# Infrastructure integration tests — require a real Postgres (e.g. via `docker compose`)
#   default test URL: postgresql+asyncpg://app_user:change_me@localhost:5433/freelance_platform_test
pytest tests/infrastructure -m integration
```

Linting and type checking:

```bash
ruff check src tests
mypy app/domain app/application
```

---

## Project layout

```text
src/app/
├── domain/            # entities, value objects, repo interfaces, domain services
├── application/       # async use cases, DTOs, authorization, shared ports
├── infrastructure/    # SQLAlchemy models+repos, migrations, JWT, Argon2, seeding
│   └── seed/          # idempotent RBAC + admin seeding
├── presentation/      # FastAPI routers, schemas, envelopes, provider stubs
│   └── core/providers.py   # DI stubs (overridden by bootstrap/container.py)
├── bootstrap/         # composition root: container.py + run.py (FastAPI entrypoint)
└── main entrypoint    # `app.bootstrap.run:app`
```

---

## Documentation index

- `ARCHITECTURE.md` — layers and dependency rules
- `DOMAIN.md` — entities, value objects, repository interfaces per context
- `APPLICATION.md` — use cases, DTOs, service ports
- `AUTHORIZATION.md` — RBAC model, permission keys, self vs. on-behalf pattern
- `API_DESIGN.md` — response envelope, error shape, pagination, routes
- `PRESENTATION.md` — FastAPI structure, DI wiring, WebSocket
- `INFRASTRUCTURE.md` — SQLAlchemy/Postgres, JWT, hashing, seed strategy
- `DOCKER.md` — containerization and seed strategy details
- `TESTING.md` — pytest rules for unit, infra, and presentation tests
- `ERROR_HANDLING.md` — exception hierarchy and HTTP status mapping