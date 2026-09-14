from dataclasses import dataclass
from datetime import datetime

from app.domain.shared.entity import Entity
from app.domain.shared.exceptions import InvalidStateTransitionError
from app.domain.shared.types import EntityId


@dataclass(eq=False)
class Category(Entity):
    parent_category_id: EntityId | None
    category_key: str
    name: str
    slug: str
    description: str | None = None
    is_active: bool = True
    sort_order: int = 0
    deleted_at: datetime | None = None

    def deactivate(self) -> None:
        self.is_active = False

    def rename(self, name: str, slug: str) -> None:
        self.name = name
        self.slug = slug

    def soft_delete(self, at: datetime) -> None:
        self.deleted_at = at
        self.is_active = False


@dataclass(eq=False)
class CategorySupervisor(Entity):
    category_id: EntityId
    supervisor_user_id: EntityId
    assigned_by_user_id: EntityId
    is_primary: bool
    is_active: bool
    assigned_at: datetime
    revoked_at: datetime | None = None

    def revoke(self, at: datetime) -> None:
        if not self.is_active:
            raise InvalidStateTransitionError(f"Supervisor link {self.id} is already revoked.")
        self.is_active = False
        self.revoked_at = at

    def promote(self) -> None:
        self.is_primary = True
