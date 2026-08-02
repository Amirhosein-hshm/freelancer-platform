from abc import ABC, abstractmethod

from app.domain.category.entities import Category, CategorySupervisor
from app.domain.shared.types import EntityId


class ICategoryRepository(ABC):
    @abstractmethod
    def add(self, category: Category) -> None: ...

    @abstractmethod
    def get_by_id(self, category_id: EntityId) -> Category:
        """Raise ``CategoryNotFoundError`` if absent."""

    @abstractmethod
    def get_by_slug(self, slug: str) -> Category:
        """Raise ``CategoryNotFoundError`` if absent."""

    @abstractmethod
    def list_active(self) -> list[Category]: ...

    @abstractmethod
    def update(self, category: Category) -> None: ...


class ICategorySupervisorRepository(ABC):
    @abstractmethod
    def add(self, link: CategorySupervisor) -> None: ...

    @abstractmethod
    def list_active_supervisors(self, category_id: EntityId) -> list[CategorySupervisor]: ...

    @abstractmethod
    def list_categories_for_supervisor(self, supervisor_user_id: EntityId) -> list[EntityId]: ...

    @abstractmethod
    def is_supervisor_of(self, supervisor_user_id: EntityId, category_id: EntityId) -> bool: ...

    @abstractmethod
    def update(self, link: CategorySupervisor) -> None: ...
