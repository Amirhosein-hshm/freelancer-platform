from app.domain.shared.types import EntityId
from app.domain.ticketing.entities import TicketMessage
from app.domain.ticketing.exceptions import TicketMessageNotFoundError
from app.domain.ticketing.repositories import ITicketMessageRepository


class FakeTicketMessageRepository(ITicketMessageRepository):
    def __init__(self) -> None:
        self._store: list[TicketMessage] = []

    async def add(self, message: TicketMessage) -> None:
        self._store.append(message)

    async def get_by_id(self, message_id: EntityId) -> TicketMessage:
        for message in self._store:
            if message.id == message_id:
                return message
        raise TicketMessageNotFoundError(f"Ticket message {message_id} not found.")

    async def list_by_ticket(self, ticket_id: EntityId) -> list[TicketMessage]:
        return sorted(
            (m for m in self._store if m.ticket_id == ticket_id),
            key=lambda m: m.sent_at,
        )

    async def list_by_file_asset_id(self, file_asset_id: EntityId) -> list[TicketMessage]:
        return [m for m in self._store if file_asset_id in m.attachment_file_asset_ids]

    async def update(self, message: TicketMessage) -> None:
        for idx, existing in enumerate(self._store):
            if existing.id == message.id:
                self._store[idx] = message
                return

    async def delete(self, message_id: EntityId) -> None:
        self._store = [m for m in self._store if m.id != message_id]
