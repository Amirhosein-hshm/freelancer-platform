# Freelance Platform API

A freelance/project marketplace backend built with FastAPI, SQLAlchemy (async), and
Postgres, following a clean/hexagonal architecture across five packages:

`domain` → `application` → `infrastructure`, with `presentation`/`bootstrap` on top.
See `ARCHITECTURE.md`, `DOMAIN.md`, and `APPLICATION.md` for details.

## Architecture

- **domain** — entities, value objects, repository interfaces, domain services. No
  framework imports.
- **application** — asynchronous use cases (Command/Query DTOs + Result DTOs, one
  `execute` per use case), authorization via `IAuthorizationService`.
- **infrastructure** — SQLAlchemy/Postgres repositories, JWT (PyJWT) + Argon2 password
  hashing, Alembic migrations, idempotent RBAC/admin seeding.
- **presentation** — FastAPI routers, response envelopes (`API_DESIGN.md`), provider
  stubs (no `infrastructure` imports).
- **bootstrap** — the composition root wiring real infrastructure into the presentation
  stubs (see `PRESENTATION.md` §3).

## Getting Started

### 1. Prerequisites

- Docker + Docker Compose
- Python >= 3.12 (for local development / running tests)

### 2. Configure environment

```bash
cp .env.example .env
# then edit .env: set a real JWT_SECRET and the initial ADMIN_PASSWORD
```

### 3. Build and run the full stack (db + migrate + seed + app)

```bash
docker compose up --build
```

Compose starts a `postgres:16-alpine` database (health-checked), runs a one-shot
`migrate` service (`alembic upgrade head` + idempotent seed), then starts the `app`
only after migration completes successfully.

### 4. Verify

- API docs: http://localhost:8000/docs
- The seeded admin can log in and confirm their roles/permissions:

```bash
# login (from your local shell, outside the container):
curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"<ADMIN_PASSWORD>"}'
```

  Then call `GET /api/v1/auth/me` with the returned `access_token` and you should see
  `roles`/`permissions` reflecting the seeded admin role.

The `.env` `ADMIN_PASSWORD` is a temporary initial credential — change it after first
login.

## Running tests

```bash
# Install dev deps
pip install -e ".[dev]"

# Domain + application unit tests (no external services)
pytest -q

# Infrastructure integration tests (real Postgres; see TESTING.md)
pytest tests/infrastructure -m integration
```