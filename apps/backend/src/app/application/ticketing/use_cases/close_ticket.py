from app.application.shared.authorization import IAuthorizationService
from app.application.shared.ports import IClock, IUnitOfWork
from app.application.shared.use_case import UseCase
from app.application.ticketing.access import ensure_party
from app.application.ticketing.dto import (
    CloseTicketCommand,
    CloseTicketResult,
)
from app.application.ticketing.permissions import (
    PERMISSION_TICKET_CLOSE_ANY,
    PERMISSION_TICKET_CLOSE_OWN,
)
from app.domain.ticketing.repositories import ITicketRepository


class CloseTicketUseCase(UseCase[CloseTicketCommand, CloseTicketResult]):
    def __init__(
        self,
        authorization_service: IAuthorizationService,
        ticket_repo: ITicketRepository,
        clock: IClock,
        uow: IUnitOfWork,
    ) -> None:
        self._authorization_service = authorization_service
        self._ticket_repo = ticket_repo
        self._clock = clock
        self._uow = uow

    async def execute(self, request: CloseTicketCommand) -> CloseTicketResult:
        ticket = await self._ticket_repo.get_by_id(request.ticket_id)
        await ensure_party(ticket, request.actor_id)
        if not await self._authorization_service.has_permission(request.actor_id, PERMISSION_TICKET_CLOSE_ANY):
            await self._authorization_service.require_permission(request.actor_id, PERMISSION_TICKET_CLOSE_OWN)
        now = await self._clock.now()
        async with self._uow:
            ticket.close(request.actor_id, now)
            await self._ticket_repo.update(ticket)
            await self._uow.commit()
        return CloseTicketResult(ticket_id=ticket.id, status=ticket.status)