from app.application.shared.use_case import UseCase
from app.application.ticketing.access import ensure_participant
from app.application.ticketing.dto import (
    GetTicketMessagesQuery,
    GetTicketMessagesResult,
)
from app.application.ticketing.mapping import to_message_result
from app.domain.ticketing.repositories import (
    ITicketMessageRepository,
    ITicketParticipantRepository,
    ITicketRepository,
)


class GetTicketMessagesUseCase(UseCase[GetTicketMessagesQuery, GetTicketMessagesResult]):
    def __init__(
        self,
        ticket_repo: ITicketRepository,
        message_repo: ITicketMessageRepository,
        participant_repo: ITicketParticipantRepository,
    ) -> None:
        self._ticket_repo = ticket_repo
        self._message_repo = message_repo
        self._participant_repo = participant_repo

    async def execute(self, request: GetTicketMessagesQuery) -> GetTicketMessagesResult:
        ticket = await self._ticket_repo.get_by_id(request.ticket_id)
        await ensure_participant(self._participant_repo, ticket.id, request.actor_id)
        messages = await self._message_repo.list_by_ticket(ticket.id)
        return GetTicketMessagesResult(messages=[to_message_result(m) for m in messages])
