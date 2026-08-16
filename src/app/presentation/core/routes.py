from fastapi.routing import APIRoute

from app.presentation.core.envelope import ErrorEnvelope


def _error_example(code: str, message: str) -> dict:
    return {
        "summary": code,
        "value": {
            "success": False,
            "error": {"code": code, "message": message, "details": None},
        },
    }


_DEFAULT_ERROR_RESPONSES = {
    400: {
        "model": ErrorEnvelope,
        "description": "Bad request / validation error",
        "content": {
            "application/json": {
                "examples": {
                    "validation": _error_example("VALIDATION", "Request validation failed."),
                }
            }
        },
    },
    401: {
        "model": ErrorEnvelope,
        "description": "Authentication required or token invalid/expired",
        "content": {
            "application/json": {
                "examples": {
                    "unauthorized": _error_example("UNAUTHORIZED", "Invalid or expired token."),
                }
            }
        },
    },
    403: {
        "model": ErrorEnvelope,
        "description": "Permission denied",
        "content": {
            "application/json": {
                "examples": {
                    "permission_denied": _error_example(
                        "PERMISSION_DENIED", "You do not have permission to perform this action."
                    ),
                }
            }
        },
    },
    404: {
        "model": ErrorEnvelope,
        "description": "Entity not found",
        "content": {
            "application/json": {
                "examples": {
                    "entity_not_found": _error_example("ENTITY_NOT_FOUND", "The requested resource was not found."),
                }
            }
        },
    },
    409: {
        "model": ErrorEnvelope,
        "description": "Conflict / invalid state transition",
        "content": {
            "application/json": {
                "examples": {
                    "invalid_state_transition": _error_example(
                        "INVALID_STATE_TRANSITION", "The requested state transition is not allowed."
                    ),
                    "unique_constraint_violation": _error_example(
                        "UNIQUE_CONSTRAINT_VIOLATION",
                        "A resource with the same unique value already exists.",
                    ),
                }
            }
        },
    },
    422: {
        "model": ErrorEnvelope,
        "description": "Business rule violation",
        "content": {
            "application/json": {
                "examples": {
                    "business_rule_violation": _error_example(
                        "BUSINESS_RULE_VIOLATION", "The operation violates a business rule."
                    ),
                }
            }
        },
    },
    500: {
        "model": ErrorEnvelope,
        "description": "Internal server error",
        "content": {
            "application/json": {
                "examples": {
                    "internal_error": _error_example("INTERNAL_ERROR", "An unexpected error occurred."),
                }
            }
        },
    },
}


def _operation_summary(operation_id: str | None) -> str | None:
    if not operation_id:
        return None
    return operation_id.replace("_", " ").strip().title()


class DocumentedAPIRoute(APIRoute):
    """APIRoute that adds OpenAPI hygiene defaults.

    - Auto-generates a ``summary`` from ``operation_id`` when not provided.
    - Merges default error response documentation (400/401/403/404/409/422/500)
      unless the route already defines its own responses for that status.
    """

    def __init__(self, *args: object, **kwargs: object) -> None:
        if kwargs.get("summary") is None and kwargs.get("operation_id"):
            kwargs["summary"] = _operation_summary(str(kwargs["operation_id"]))

        route_responses = kwargs.get("responses") or {}
        merged_responses: dict[int, dict] = {}
        for status, spec in _DEFAULT_ERROR_RESPONSES.items():
            if status not in route_responses:
                merged_responses[status] = spec
        if route_responses:
            merged_responses.update(route_responses)  # type: ignore[arg-type]
        kwargs["responses"] = merged_responses

        super().__init__(*args, **kwargs)
