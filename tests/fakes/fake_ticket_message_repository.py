from app.domain.shared.types import EntityId
from app.domain.ticketing.entities import TicketMessage
from app.domain.ticketing.repositories import ITicketMessageRepository


class FakeTicketMessageRepository(ITicketMessageRepository):
    def __init__(self) -> None:
        self._store: list[TicketMessage] = []

    async def add(self, message: TicketMessage) -> None:
        self._store.append(message)

    async def list_by_ticket(self, ticket_id: EntityId) -> list[TicketMessage]:
        return sorted(
            (m for m in self._store if m.ticket_id == ticket_id),
            key=lambda m: m.sent_at,
        )
