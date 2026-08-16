from dataclasses import dataclass
from datetime import datetime

from app.application.shared.exceptions import ValidationError
from app.domain.shared.types import EntityId


@dataclass(frozen=True)
class CategoryResult:
    category_id: EntityId
    category_key: str
    name: str
    slug: str
    description: str | None
    is_active: bool
    sort_order: int
    parent_category_id: EntityId | None


@dataclass(frozen=True)
class CreateCategoryCommand:
    actor_id: EntityId
    name: str
    slug: str
    category_key: str
    description: str | None = None
    parent_category_id: EntityId | None = None
    sort_order: int = 0

    def validate(self) -> None:
        if not self.name.strip() or not self.slug.strip() or not self.category_key.strip():
            raise ValidationError("name, slug and category_key are required.")


@dataclass(frozen=True)
class UpdateCategoryCommand:
    actor_id: EntityId
    category_id: EntityId
    name: str
    slug: str
    description: str | None = None
    sort_order: int = 0

    def validate(self) -> None:
        if not self.name.strip() or not self.slug.strip():
            raise ValidationError("name and slug are required.")


@dataclass(frozen=True)
class DeleteCategoryCommand:
    actor_id: EntityId
    category_id: EntityId


@dataclass(frozen=True)
class DeleteCategoryResult:
    category_id: EntityId


@dataclass(frozen=True)
class AssignSupervisorCommand:
    actor_id: EntityId
    category_id: EntityId
    supervisor_user_id: EntityId


@dataclass(frozen=True)
class AssignSupervisorResult:
    link_id: EntityId
    category_id: EntityId
    supervisor_user_id: EntityId


@dataclass(frozen=True)
class RemoveSupervisorCommand:
    actor_id: EntityId
    category_id: EntityId
    supervisor_user_id: EntityId


@dataclass(frozen=True)
class RemoveSupervisorResult:
    category_id: EntityId
    supervisor_user_id: EntityId
    revoked_at: datetime


@dataclass(frozen=True)
class GetCategoriesQuery:
    pass


@dataclass(frozen=True)
class GetCategoriesResult:
    categories: list[CategoryResult]


@dataclass(frozen=True)
class GetCategoryQuery:
    category_id: EntityId


@dataclass(frozen=True)
class GetCategoryResult(CategoryResult):
    pass


@dataclass(frozen=True)
class CategorySupervisorResult:
    link_id: EntityId
    category_id: EntityId
    supervisor_user_id: EntityId
    is_primary: bool
    assigned_at: datetime


@dataclass(frozen=True)
class ListCategorySupervisorsQuery:
    category_id: EntityId


@dataclass(frozen=True)
class ListCategorySupervisorsResult:
    supervisors: list[CategorySupervisorResult]
