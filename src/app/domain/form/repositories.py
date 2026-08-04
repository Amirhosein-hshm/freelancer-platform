from abc import ABC, abstractmethod

from app.domain.form.entities import FormTemplate
from app.domain.shared.types import EntityId


class IFormTemplateRepository(ABC):
    @abstractmethod
    async def add(self, template: FormTemplate) -> None: ...

    @abstractmethod
    async def get_by_id(self, template_id: EntityId) -> FormTemplate:
        """Raise ``FormTemplateNotFoundError`` if absent."""

    @abstractmethod
    async def get_published_for_category(self, category_id: EntityId) -> FormTemplate:
        """Raise ``FormTemplateNotFoundError`` if no published template exists."""

    @abstractmethod
    async def update(self, template: FormTemplate) -> None: ...

    @abstractmethod
    async def list_versions(self, category_id: EntityId) -> list[FormTemplate]: ...
