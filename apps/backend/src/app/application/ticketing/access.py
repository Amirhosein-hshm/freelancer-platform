from app.domain.shared.types import EntityId
from app.domain.ticketing.entities import Ticket
from app.domain.ticketing.exceptions import NotTicketPartyError


async def ensure_party(ticket: Ticket, actor_id: EntityId) -> None:
    if not ticket.is_party(actor_id):
        raise NotTicketPartyError(f"User {actor_id} is not a party of ticket {ticket.id}.")