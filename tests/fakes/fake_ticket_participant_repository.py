from app.domain.shared.types import EntityId
from app.domain.ticketing.entities import TicketParticipant
from app.domain.ticketing.repositories import ITicketParticipantRepository


class FakeTicketParticipantRepository(ITicketParticipantRepository):
    async def __init__(self) -> None:
        self._store: list[TicketParticipant] = []

    async def add(self, participant: TicketParticipant) -> None:
        self._store.append(participant)

    async def list_by_ticket(self, ticket_id: EntityId) -> list[TicketParticipant]:
        return [p for p in self._store if p.ticket_id == ticket_id]

    async def is_participant(self, ticket_id: EntityId, user_id: EntityId) -> bool:
        return any(
            p.ticket_id == ticket_id
            and p.user_id == user_id
            and p.left_at is None
            for p in self._store
        )
