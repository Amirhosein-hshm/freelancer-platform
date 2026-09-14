from abc import ABC, abstractmethod

from app.domain.category.entities import Category, CategorySupervisor
from app.domain.shared.types import EntityId


class ICategoryRepository(ABC):
    @abstractmethod
    async def add(self, category: Category) -> None: ...

    @abstractmethod
    async def get_by_id(self, category_id: EntityId) -> Category:
        """Raise ``CategoryNotFoundError`` if absent."""

    @abstractmethod
    async def get_by_slug(self, slug: str) -> Category:
        """Raise ``CategoryNotFoundError`` if absent."""

    @abstractmethod
    async def list_active(
        self,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[Category]: ...

    @abstractmethod
    async def count_active(self) -> int: ...

    @abstractmethod
    async def list_by_parent_id(self, parent_category_id: EntityId) -> list[Category]: ...

    @abstractmethod
    async def update(self, category: Category) -> None: ...


class ICategorySupervisorRepository(ABC):
    @abstractmethod
    async def add(self, link: CategorySupervisor) -> None: ...

    @abstractmethod
    async def list_active_supervisors(self, category_id: EntityId) -> list[CategorySupervisor]: ...

    @abstractmethod
    async def list_categories_for_supervisor(self, supervisor_user_id: EntityId) -> list[EntityId]: ...

    @abstractmethod
    async def is_supervisor_of(self, supervisor_user_id: EntityId, category_id: EntityId) -> bool: ...

    @abstractmethod
    async def update(self, link: CategorySupervisor) -> None: ...
