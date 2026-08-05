from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class PaginationMeta(BaseModel):
    page: int
    page_size: int
    total_items: int
    total_pages: int


class SuccessEnvelope(BaseModel, Generic[T]):  # noqa: UP046  (pydantic v2 needs typing.Generic, not PEP 695)
    success: bool = True
    message: str
    data: T
    meta: PaginationMeta | None = None


class ErrorDetail(BaseModel):
    code: str
    message: str
    details: dict | list | None = None


class ErrorEnvelope(BaseModel):
    success: bool = False
    error: ErrorDetail