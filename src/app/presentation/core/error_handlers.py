import logging
import re

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.application.shared.exceptions import ExternalServiceError, PermissionDeniedError, ValidationError
from app.domain.shared.exceptions import (
    BusinessRuleViolationError,
    EntityNotFoundError,
    InvalidStateTransitionError,
    UniqueConstraintViolationError,
)
from app.presentation.core.envelope import ErrorDetail, ErrorEnvelope

logger = logging.getLogger(__name__)


def to_error_code(exc: type[BaseException]) -> str:
    name = exc.__name__.removesuffix("Error")
    return re.sub(r"(?<!^)(?=[A-Z])", "_", name).upper()


def _envelope(exc: Exception, status: int, details: dict | list | None = None) -> JSONResponse:
    return JSONResponse(
        status_code=status,
        content=ErrorEnvelope(
            error=ErrorDetail(code=to_error_code(type(exc)), message=str(exc), details=details)
        ).model_dump(),
    )


def _envelope_serializer() -> JSONResponse:
    return JSONResponse(
        status_code=500,
        content=ErrorEnvelope(
            error=ErrorDetail(code="INTERNAL_ERROR", message="Internal server error.")
        ).model_dump(),
    )


def register_exception_handlers(app: FastAPI) -> None:
    async def _entity_not_found(_: Request, exc: Exception) -> JSONResponse:
        return _envelope(exc, 404)

    async def _invalid_state(_: Request, exc: Exception) -> JSONResponse:
        return _envelope(exc, 409)

    async def _business_rule(_: Request, exc: Exception) -> JSONResponse:
        return _envelope(exc, 422)

    async def _unique_constraint(_: Request, exc: Exception) -> JSONResponse:
        return _envelope(exc, 409)

    async def _permission_denied(_: Request, exc: Exception) -> JSONResponse:
        return _envelope(exc, 403)

    async def _validation(_: Request, exc: Exception) -> JSONResponse:
        return _envelope(exc, 400)

    async def _external_service(_: Request, exc: Exception) -> JSONResponse:
        return _envelope(exc, 502)

    async def _unhandled(_: Request, exc: Exception) -> JSONResponse:
        logger.error("Unhandled exception", exc_info=exc)
        return _envelope_serializer()

    app.add_exception_handler(EntityNotFoundError, _entity_not_found)
    app.add_exception_handler(InvalidStateTransitionError, _invalid_state)
    app.add_exception_handler(BusinessRuleViolationError, _business_rule)
    app.add_exception_handler(UniqueConstraintViolationError, _unique_constraint)
    app.add_exception_handler(PermissionDeniedError, _permission_denied)
    app.add_exception_handler(ValidationError, _validation)
    app.add_exception_handler(ExternalServiceError, _external_service)
    app.add_exception_handler(Exception, _unhandled)