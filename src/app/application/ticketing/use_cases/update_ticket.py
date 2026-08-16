from app.application.shared.authorization import (
    IAuthorizationService,
    authorize_owned_action,
)
from app.application.shared.ports import IClock, IUnitOfWork
from app.application.shared.use_case import UseCase
from app.application.ticketing.dto import UpdateTicketCommand, UpdateTicketResult
from app.application.ticketing.permissions import (
    PERMISSION_TICKET_MANAGE_ANY,
    PERMISSION_TICKET_MANAGE_OWN,
)
from app.domain.ticketing.enums import TicketStatus
from app.domain.ticketing.repositories import ITicketRepository


class UpdateTicketUseCase(UseCase[UpdateTicketCommand, UpdateTicketResult]):
    def __init__(
        self,
        ticket_repo: ITicketRepository,
        authorization_service: IAuthorizationService,
        clock: IClock,
        uow: IUnitOfWork,
    ) -> None:
        self._ticket_repo = ticket_repo
        self._authorization_service = authorization_service
        self._clock = clock
        self._uow = uow

    async def execute(self, request: UpdateTicketCommand) -> UpdateTicketResult:
        ticket = await self._ticket_repo.get_by_id(request.ticket_id)
        await authorize_owned_action(
            self._authorization_service,
            request.actor_id,
            ticket.created_by_user_id,
            PERMISSION_TICKET_MANAGE_OWN,
            PERMISSION_TICKET_MANAGE_ANY,
        )
        now = await self._clock.now()
        if request.subject is not None:
            ticket.update_subject(request.subject)
        if request.priority is not None:
            ticket.set_priority(request.priority)
        if request.status is not None:
            if request.status == TicketStatus.CLOSED:
                ticket.close(request.actor_id, now)
            elif request.status == TicketStatus.ARCHIVED:
                ticket.archive(request.actor_id, now)
            elif request.status == TicketStatus.OPEN and ticket.status == TicketStatus.CLOSED:
                ticket.reopen()
            else:
                ticket.transition_to(request.status)
        async with self._uow:
            await self._ticket_repo.update(ticket)
            await self._uow.commit()
        return UpdateTicketResult(ticket_id=ticket.id, status=ticket.status)
