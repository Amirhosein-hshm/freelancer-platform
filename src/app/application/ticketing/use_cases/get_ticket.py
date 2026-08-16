from app.application.shared.authorization import IAuthorizationService
from app.application.shared.use_case import UseCase
from app.application.ticketing.access import ensure_participant
from app.application.ticketing.dto import GetTicketQuery, GetTicketResult
from app.application.ticketing.mapping import to_ticket_result
from app.application.ticketing.permissions import PERMISSION_TICKET_READ_ANY
from app.domain.ticketing.repositories import (
    ITicketParticipantRepository,
    ITicketRepository,
)


class GetTicketUseCase(UseCase[GetTicketQuery, GetTicketResult]):
    def __init__(
        self,
        ticket_repo: ITicketRepository,
        participant_repo: ITicketParticipantRepository,
        authorization_service: IAuthorizationService,
    ) -> None:
        self._ticket_repo = ticket_repo
        self._participant_repo = participant_repo
        self._authorization_service = authorization_service

    async def execute(self, request: GetTicketQuery) -> GetTicketResult:
        ticket = await self._ticket_repo.get_by_id(request.ticket_id)
        if not await self._authorization_service.has_permission(request.actor_id, PERMISSION_TICKET_READ_ANY):
            await ensure_participant(self._participant_repo, ticket.id, request.actor_id)
        return GetTicketResult(ticket=to_ticket_result(ticket))
