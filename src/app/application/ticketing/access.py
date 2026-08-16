from app.domain.shared.types import EntityId
from app.domain.ticketing.exceptions import NotTicketParticipantError
from app.domain.ticketing.repositories import ITicketParticipantRepository


async def ensure_participant(
    participant_repo: ITicketParticipantRepository,
    ticket_id: EntityId,
    actor_id: EntityId,
) -> None:
    if not await participant_repo.is_participant(ticket_id, actor_id):
        raise NotTicketParticipantError(f"User {actor_id} is not a participant of ticket {ticket_id}.")
