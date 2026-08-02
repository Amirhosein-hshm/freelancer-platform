from app.domain.shared.types import EntityId
from app.domain.ticketing.entities import Ticket
from app.domain.ticketing.exceptions import TicketNotFoundError
from app.domain.ticketing.repositories import ITicketRepository


class FakeTicketRepository(ITicketRepository):
    def __init__(self) -> None:
        self._store: dict[str, Ticket] = {}

    def add(self, ticket: Ticket) -> None:
        self._store[ticket.id] = ticket

    def get_by_id(self, ticket_id: EntityId) -> Ticket:
        try:
            return self._store[ticket_id]
        except KeyError:
            raise TicketNotFoundError(f"Ticket {ticket_id} not found.") from None

    def get_by_code(self, ticket_code: str) -> Ticket:
        for ticket in self._store.values():
            if ticket.ticket_code == ticket_code:
                return ticket
        raise TicketNotFoundError(f"Ticket with code {ticket_code} not found.")

    def list_for_user(self, user_id: EntityId) -> list[Ticket]:
        return [
            ticket
            for ticket in self._store.values()
            if (ticket.created_by_user_id == user_id
                or ticket.assigned_to_user_id == user_id)
            and ticket.deleted_at is None
        ]

    def update(self, ticket: Ticket) -> None:
        self._store[ticket.id] = ticket
