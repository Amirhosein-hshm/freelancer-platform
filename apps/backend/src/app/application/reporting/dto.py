from dataclasses import dataclass

from app.domain.shared.types import EntityId


@dataclass(frozen=True)
class ReportingQuery:
    actor_id: EntityId
