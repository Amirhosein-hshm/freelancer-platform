from app.domain.shared.types import EntityId
from app.domain.ticketing.entities import Ticket
from app.domain.ticketing.exceptions import TicketNotFoundError
from app.domain.ticketing.repositories import ITicketRepository


class FakeTicketRepository(ITicketRepository):
    """Mirrors the SQLAlchemy repository: every read excludes soft-deleted tickets."""

    def __init__(self) -> None:
        self._store: dict[str, Ticket] = {}

    async def add(self, ticket: Ticket) -> None:
        self._store[ticket.id] = ticket

    async def get_by_id(self, ticket_id: EntityId) -> Ticket:
        ticket = self._store.get(ticket_id)
        if ticket is None or ticket.deleted_at is not None:
            raise TicketNotFoundError(f"Ticket {ticket_id} not found.")
        return ticket

    async def get_by_code(self, ticket_code: str) -> Ticket:
        for ticket in self._store.values():
            if ticket.ticket_code == ticket_code and ticket.deleted_at is None:
                return ticket
        raise TicketNotFoundError(f"Ticket with code {ticket_code} not found.")

    async def list_for_user(self, user_id: EntityId) -> list[Ticket]:
        return [
            ticket
            for ticket in self._store.values()
            if (ticket.created_by_user_id == user_id or ticket.assigned_to_user_id == user_id)
            and ticket.deleted_at is None
        ]

    async def update(self, ticket: Ticket) -> None:
        self._store[ticket.id] = ticket
