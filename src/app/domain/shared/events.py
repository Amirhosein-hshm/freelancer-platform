from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class DomainEvent(ABC):  # noqa: B024 - intentionally abstract base
    occurred_at: datetime


class IEventPublisher(ABC):
    @abstractmethod
    def publish(self, events: list[DomainEvent]) -> None: ...
