from abc import ABC
from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING

from app.domain.shared.types import EntityId

if TYPE_CHECKING:
    from app.domain.shared.events import DomainEvent


@dataclass(eq=False)
class Entity(ABC):  # noqa: B024 - intentionally abstract base, no abstract members
    """Base entity: identity is defined solely by ``id``.

    Subclasses must be declared with ``@dataclass(eq=False)`` so that equality and
    hashing are inherited from this base (identity-based) instead of being regenerated
    over all fields.
    """

    id: EntityId
    created_at: datetime
    updated_at: datetime | None = None

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Entity):
            return False
        return self.id == other.id

    def __hash__(self) -> int:
        return hash(self.id)


@dataclass(eq=False)
class AggregateRoot(Entity):  # noqa: B024 - intentionally abstract base
    _domain_events: list["DomainEvent"] = field(default_factory=list, init=False, repr=False)

    def pull_domain_events(self) -> list["DomainEvent"]:
        events = self._domain_events
        self._domain_events = []
        return events

    def _record_event(self, event: "DomainEvent") -> None:
        self._domain_events.append(event)
