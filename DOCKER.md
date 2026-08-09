# DOCKER.md — Containerization and Seed Strategy

## 1. Goal

The project must spin up completely with a single `docker compose up`: the database is created, migrations are executed, roles/permissions/admin are seeded, and the FastAPI app becomes accessible on the designated port — without any manual steps.

## 2. Best Practices Followed (and Why)

### a) Migrations and Seeds are separated, but both run before the app

- **Migration (Alembic)** builds/modifies table structures — version-controlled, reversible, located in `infrastructure/migrations/versions/`.
- **Seed** only populates reference data (roles, permissions, admin) — idempotent Python code in `infrastructure/seed/`.

We do not mix these two (i.e., we didn't write the seed inside a migration) because: migrations must remain schema-only so rollback/diff stays clean; seeds need to evolve independently of the schema (e.g., adding a new permission) without requiring a new migration.

### b) A separate one-shot service for migrate+seed, not inside the app itself

If we place migration/seed inside the FastAPI app's startup event, when scaling out to multiple replicas later, all replicas will simultaneously try to migrate/seed → race condition on the schema. The industry-standard solution: a distinct service in `docker-compose` (`migrate`) that runs once, completes its work, and exits; the `app` service uses `depends_on: condition: service_completed_successfully` to wait until `migrate` finishes successfully.

### c) Idempotency in seed scripts, not "run only the first time"

Instead of attempting to detect "is this the first run?", we write the seed script so that repeated executions are safe and have no redundant side effects (`ON CONFLICT DO NOTHING` for roles/permissions, `if not exists` check for admin). This means even if we restart `compose`, the seed runs again without producing duplicate data or errors — which is far more reliable than relying on an external flag/state ("has it been seeded before?").

### d) Admin credentials from env, not hardcoded

`ADMIN_EMAIL` and `ADMIN_PASSWORD` are defined in `.env` (which is in `.gitignore`), not in the code or committed `docker-compose.yml`. An `.env.example` file with placeholder values is committed to Git. After the initial spin-up, standard security recommendations dictate that the admin changes their password from the panel (documented in `README.md` that this initial password is temporary).

### e) Health check on Postgres

`app` and `migrate` shouldn't just wait for "the Postgres container started" — they must wait for "Postgres is actually ready to accept connections." This is guaranteed using a `healthcheck` on the `db` service along with `depends_on: condition: service_healthy`.

---

## 3. File Structure

```text
project_root/
├── Dockerfile
├── docker-compose.yml
├── .env.example
├── .dockerignore
└── src/app/infrastructure/seed/run_seed.py   (already covered in INFRASTRUCTURE.md)

```

---

## 4. Dockerfile (multi-stage, non-root)

```dockerfile
# ---- builder ----
FROM python:3.12-slim AS builder
WORKDIR /build
RUN pip install --no-cache-dir --upgrade pip
COPY pyproject.toml .
RUN pip install --no-cache-dir --prefix=/install .

# ---- runtime ----
FROM python:3.12-slim
RUN useradd --create-home appuser
WORKDIR /app
COPY --from=builder /install /usr/local
COPY src/ ./src/
COPY alembic.ini ./
USER appuser
EXPOSE 8000
# app.bootstrap.run:app — NOT app.presentation.main:app — because presentation/main.py only
# builds the FastAPI app with provider *stubs*; app.bootstrap.run is the composition root
# that wires in the real infrastructure implementations (see PRESENTATION.md §3).
CMD ["uvicorn", "app.bootstrap.run:app", "--host", "0.0.0.0", "--port", "8000"]

```

**Notes:** Multi-stage build reduces the final image size (build tools are excluded from the final image); `USER appuser` ensures the container does not run as root (a basic security best practice).

---

## 5. docker-compose.yml (Outline — exact implementation to be finalized by opencode)

```yaml
services:
  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: ${POSTGRES_DB}
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - db_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER}"]
      interval: 5s
      timeout: 5s
      retries: 10
    ports:
      - "5432:5432"

  migrate:
    build: .
    command: sh -c "alembic upgrade head && python -m app.infrastructure.seed.run_seed"
    env_file: .env
    depends_on:
      db:
        condition: service_healthy

  app:
    build: .
    env_file: .env
    ports:
      - "8000:8000"
    depends_on:
      migrate:
        condition: service_completed_successfully

volumes:
  db_data:
```

---

## 6. .env.example

```env
POSTGRES_DB=freelance_platform
POSTGRES_USER=app_user
POSTGRES_PASSWORD=change_me
DATABASE_URL=postgresql+asyncpg://app_user:change_me@db:5432/freelance_platform
JWT_SECRET=change_me_to_a_long_random_string
JWT_ACCESS_TTL_MINUTES=15
JWT_REFRESH_TTL_DAYS=30
ADMIN_EMAIL=admin@example.com
ADMIN_PASSWORD=change_me_strong_password
CORS_ALLOWED_ORIGINS=http://localhost:3000

```

---

## 7. .dockerignore

```text
.venv/
__pycache__/
*.pyc
.git/
tests/
.env

```

---

## 8. What We Intentionally Omit (KISS Principle)

- **Redis:** Only needed if we eventually require multiple app replicas or cache/pub-sub. For now, in-memory WebSocket state on a single instance is sufficient.
- **Nginx/reverse proxy in compose:** Not needed in dev environment; in actual production, it will be placed behind a separate reverse proxy/ingress, which is outside the scope of this development compose file.
- **Celery/task queue:** We have no heavy async tasks (like sending real emails) in Phase 1.
