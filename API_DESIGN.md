# API_DESIGN.md — API Design Standard (Presentation Layer)

This document complements `ERROR_HANDLING.md` — that document defines which Exception maps to which HTTP status; this document defines the **exact JSON shape** of requests and responses.

## 1. General Principle

The client should never have to guess whether a response was successful — the `success` field is always explicit. Data, metadata (pagination), and the message are always located in a fixed place, regardless of what the endpoint returns.

## 2. Success Envelope (`SuccessEnvelope`)

```json
{
  "success": true,
  "message": "string, human-readable, always present",
  "data": "<Serialized Result DTO, array, or null for 204>",
  "meta": "<Pagination object only for list responses, otherwise null>"
}
```

Implementation as a generic Pydantic model:

```python
# presentation/core/envelope.py
from typing import Generic, TypeVar
from pydantic import BaseModel

T = TypeVar("T")

class PaginationMeta(BaseModel):
    page: int
    page_size: int
    total_items: int
    total_pages: int

class SuccessEnvelope(BaseModel, Generic[T]):
    success: bool = True
    message: str
    data: T
    meta: PaginationMeta | None = None
```

Each endpoint is documented with `response_model=SuccessEnvelope[ProjectResponse]` (or `SuccessEnvelope[list[ProjectResponse]]` for list endpoints).

## 3. Error Envelope (`ErrorEnvelope`)

```json
{
  "success": false,
  "error": {
    "code": "PROJECT_NOT_FOUND",
    "message": "Project with id 'xyz' was not found.",
    "details": null
  }
}
```

```python
class ErrorDetail(BaseModel):
    code: str
    message: str
    details: dict | list | None = None

class ErrorEnvelope(BaseModel):
    success: bool = False
    error: ErrorDetail
```

### Rule for generating `code`

`code` = the domain/application Exception class name converted to `UPPER_SNAKE_CASE`, with the `Error` suffix removed:

`ProjectNotFoundError` → `PROJECT_NOT_FOUND`, `PermissionDeniedError` → `PERMISSION_DENIED`.

This mapping is performed **automatically** inside the Exception Handler (via a `to_error_code(exc)` function), not through a manually maintained dictionary that must be updated every time.

### `details` for validation errors

```json
{
  "code": "FORM_VALIDATION_ERROR",
  "message": "Submitted form values are invalid.",
  "details": [{ "field_id": "budget", "reason": "value must be a number" }]
}
```

## 4. Exception → HTTP status mapping (reference from `ERROR_HANDLING.md`)

| Base class                                | HTTP                                                                                 |
| ----------------------------------------- | ------------------------------------------------------------------------------------ |
| `EntityNotFoundError`                     | 404                                                                                  |
| `InvalidStateTransitionError`             | 409                                                                                  |
| `BusinessRuleViolationError`              | 422                                                                                  |
| `UniqueConstraintViolationError`          | 409                                                                                  |
| `PermissionDeniedError`                   | 403                                                                                  |
| `ValidationError` / `FormValidationError` | 400                                                                                  |
| `ExternalServiceError`                    | 502                                                                                  |
| Any unknown Exception                     | 500 (+ error log, `code="INTERNAL_ERROR"`, generic message without internal details) |

Implementation: register one exception handler per base class in FastAPI (not one per concrete subclass). Since `isinstance` works across the inheritance hierarchy, there is no need to register every specific Exception (`ProjectLockedError`, etc.).

## 5. Pagination

Standard query parameters for all list endpoints: `page` (default: 1), `page_size` (default: 20, maximum: 100).

Repository `list_*` interfaces should accept `limit`/`offset` and return `(items, total_count)`.

If the repository currently returns all records, real SQL `LIMIT`/`OFFSET` must be implemented in the infrastructure layer. The presentation layer must **not** slice an already fully loaded result, since that still requires fetching the entire table into memory.

## 6. Authentication and `role`/`permission`

- Access token is sent in the header: `Authorization: Bearer <token>`.
- **One dedicated endpoint**: `GET /api/v1/auth/me`

  ```json
  {
    "success": true,
    "message": "Current user.",
    "data": {
      "user_id": "...",
      "email": "...",
      "roles": ["customer"],
      "permissions": ["project.create_own", "project.apply", ...]
    },
    "meta": null
  }
  ```

`permissions` are computed by `IAuthorizationService` (the union of all permissions granted by the user's active roles), not from the JWT. The JWT carries only roles (keeping it lightweight), while permissions may change between token issuance and consumption.

All other endpoints must **never** include `roles` or `permissions` in their `data`. This is exclusive to `/auth/me`.

## 7. Route naming and versioning

- Prefix: `/api/v1`.
- Use plural resource names following standard REST conventions: `GET /projects`, `GET /projects/{id}`, `POST /projects`.
- Non-CRUD actions are exposed as verb-based sub-routes on the resource identifier: `POST /projects/{id}/publish`, `POST /projects/{id}/cancel`, `POST /project-applications/{id}/accept`.
- Query filters remain simple and flat: `GET /projects?status=PUBLISHED&category_id=...`.
- Each router is organized by bounded context and assigned a `tags=["Project"]`.

## 8. OpenAPI / Swagger

- Use an explicit, concise `operation_id` for every endpoint (`create_project`, not FastAPI's automatically generated long name), either through a custom `generate_unique_id_function` or by specifying `operation_id` on each route.
- Every endpoint should include at least one example (`response_model` + `openapi_extra` examples) for non-obvious fields (such as enums and dates).
- Expected errors should be documented in `responses={404: {...}, 409: {...}}` (at minimum, the common errors for each resource—not necessarily all 15 Exceptions).
- Provide a brief `description` for every endpoint, derived from the Purpose section in `APPLICATION.md`.

## 9. Request Contract (Request Schemas)

Each Pydantic Request Schema contains only the fields that originate from the HTTP request body.

`actor_id` is never accepted from the JSON body; it is always extracted from the authentication dependency (`get_current_user`) and injected into the Command.

This means the Pydantic Request Schema and the Application Command DTO are **not the same object**. A small mapping function in each router is responsible for connecting them (see `PRESENTATION.md` §4).
