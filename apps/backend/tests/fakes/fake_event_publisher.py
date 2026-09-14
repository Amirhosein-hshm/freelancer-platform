from app.domain.shared.events import DomainEvent, IEventPublisher


class FakeEventPublisher(IEventPublisher):
    def __init__(self) -> None:
        self.published: list[list[DomainEvent]] = []

    def publish(self, events: list[DomainEvent]) -> None:
        if events:
            self.published.append(list(events))

    @property
    def all_events(self) -> list[DomainEvent]:
        return [event for batch in self.published for event in batch]
