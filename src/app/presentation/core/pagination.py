from fastapi import Query
from pydantic import BaseModel

from app.presentation.core.envelope import PaginationMeta


class PageQuery(BaseModel):
    page: int = Query(1, ge=1)
    page_size: int = Query(20, ge=1, le=100)

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size


def paginate[T](items: list[T], pagination: PageQuery) -> tuple[list[T], PaginationMeta]:
    """Return a page slice and pagination metadata for an in-memory list."""
    total_items = len(items)
    total_pages = max(1, (total_items + pagination.page_size - 1) // pagination.page_size)
    page = min(pagination.page, total_pages) if total_items > 0 else pagination.page
    offset = pagination.offset if page == pagination.page else (page - 1) * pagination.page_size
    page_items = items[offset : offset + pagination.page_size]
    meta = PaginationMeta(
        page=page,
        page_size=pagination.page_size,
        total_items=total_items,
        total_pages=total_pages,
    )
    return page_items, meta
