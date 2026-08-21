"""Shared DB-level pagination helpers.

Every list use case takes 1-based ``page``/``page_size`` in its Query DTO and returns
``total_items``/``page``/``page_size`` in its Result DTO; the repository receives SQL
``limit``/``offset``. Presentation turns the Result fields into a ``PaginationMeta``.

This replaces the earlier in-memory ``paginate()`` slicing for filtered endpoints: filters and
paging both run in SQL so a page is a true page of the filtered set.
"""

DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100


def limit_offset(page: int, page_size: int) -> tuple[int, int]:
    """Convert 1-based ``page``/``page_size`` into SQL ``(limit, offset)``.

    Values are clamped rather than rejected: presentation already validates ranges via
    ``PageQuery`` (``ge=1``, ``le=100``), so this is defence for direct use-case callers.
    """
    safe_page = max(1, page)
    safe_page_size = min(max(1, page_size), MAX_PAGE_SIZE)
    return safe_page_size, (safe_page - 1) * safe_page_size


def total_pages(total_items: int, page_size: int) -> int:
    """Page count for pagination metadata; always at least 1 so an empty list reads sanely."""
    safe_page_size = min(max(1, page_size), MAX_PAGE_SIZE)
    return max(1, (total_items + safe_page_size - 1) // safe_page_size)
