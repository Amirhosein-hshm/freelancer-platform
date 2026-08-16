from app.application.shared.authorization import IAuthorizationService
from app.application.shared.use_case import UseCase
from app.application.ticketing.access import ensure_participant
from app.application.ticketing.dto import (
    ListTicketParticipantsQuery,
    ListTicketParticipantsResult,
)
from app.application.ticketing.mapping import to_participant_result
from app.application.ticketing.permissions import PERMISSION_TICKET_READ_ANY
from app.domain.ticketing.repositories import (
    ITicketParticipantRepository,
    ITicketRepository,
)


class ListTicketParticipantsUseCase(UseCase[ListTicketParticipantsQuery, ListTicketParticipantsResult]):
    def __init__(
        self,
        ticket_repo: ITicketRepository,
        participant_repo: ITicketParticipantRepository,
        authorization_service: IAuthorizationService,
    ) -> None:
        self._ticket_repo = ticket_repo
        self._participant_repo = participant_repo
        self._authorization_service = authorization_service

    async def execute(self, request: ListTicketParticipantsQuery) -> ListTicketParticipantsResult:
        ticket = await self._ticket_repo.get_by_id(request.ticket_id)
        if not await self._authorization_service.has_permission(request.actor_id, PERMISSION_TICKET_READ_ANY):
            await ensure_participant(self._participant_repo, ticket.id, request.actor_id)
        participants = await self._participant_repo.list_by_ticket(ticket.id)
        return ListTicketParticipantsResult(participants=[to_participant_result(p) for p in participants])
