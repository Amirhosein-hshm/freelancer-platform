# presentation (Phase 2)

In Phase One this package is intentionally empty. Per `AGENTS.md` §2, no real code
(FastAPI routes, Pydantic schemas, JWT library calls) is written here.

Planned implementations here:

- **Routers** per bounded context (IAM, freelancer, category, form, project, review,
  feedback, ticketing, reporting), mapping HTTP requests to application DTOs/Use Cases.
- **Schemas**: Pydantic request/response models mapped to `application/<context>/dto.py`
  DTOs (not replacing them).
- **Composition root** (`container.py`): dependency injection wiring of every Port with
  the real `infrastructure` implementations.
- **Middleware / Global Exception Handler** (`error_handlers.py`): maps the exception
  hierarchy to HTTP status codes exactly as specified in `ERROR_HANDLING.md` §7.
