from abc import ABC, abstractmethod

from app.domain.form.entities import FormTemplate
from app.domain.form.enums import FormTemplateStatus
from app.domain.shared.types import EntityId


class IFormTemplateRepository(ABC):
    """All read methods exclude soft-deleted templates (``deleted_at IS NULL``)."""

    @abstractmethod
    async def add(self, template: FormTemplate) -> None: ...

    @abstractmethod
    async def get_by_id(self, template_id: EntityId) -> FormTemplate:
        """Raise ``FormTemplateNotFoundError`` if absent."""

    @abstractmethod
    async def get_published_for_category(self, category_id: EntityId) -> FormTemplate:
        """Raise ``FormTemplateNotFoundError`` if no published template exists."""

    @abstractmethod
    async def update(self, template: FormTemplate) -> None:
        """Also the persistence path for soft deletion (``FormTemplate.soft_delete``)."""

    @abstractmethod
    async def list_versions(self, category_id: EntityId, template_key: str) -> list[FormTemplate]: ...

    @abstractmethod
    async def list_templates(
        self,
        category_id: EntityId | None = None,
        status: FormTemplateStatus | None = None,
        search: str | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> list[FormTemplate]:
        """List templates across ALL categories, newest first.

        Distinct from ``list_versions``, which lists the versions of ONE template key within
        one category. Filters are applied in SQL; ``search`` is a case-insensitive substring
        match on ``name``.
        """

    @abstractmethod
    async def count_templates(
        self,
        category_id: EntityId | None = None,
        status: FormTemplateStatus | None = None,
        search: str | None = None,
    ) -> int:
        """Total matching ``list_templates``' filters, for pagination metadata."""
