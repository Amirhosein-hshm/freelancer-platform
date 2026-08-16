from app.application.shared.authorization import IAuthorizationService
from app.application.shared.exceptions import PermissionDeniedError
from app.application.shared.ports import IClock, IUnitOfWork
from app.application.shared.use_case import UseCase
from app.application.ticketing.access import ensure_participant
from app.application.ticketing.dto import (
    UpdateTicketMessageCommand,
    UpdateTicketMessageResult,
)
from app.application.ticketing.permissions import PERMISSION_TICKET_MANAGE_ANY
from app.domain.ticketing.repositories import (
    ITicketMessageRepository,
    ITicketParticipantRepository,
    ITicketRepository,
)


class UpdateTicketMessageUseCase(UseCase[UpdateTicketMessageCommand, UpdateTicketMessageResult]):
    def __init__(
        self,
        ticket_repo: ITicketRepository,
        message_repo: ITicketMessageRepository,
        participant_repo: ITicketParticipantRepository,
        authorization_service: IAuthorizationService,
        clock: IClock,
        uow: IUnitOfWork,
    ) -> None:
        self._ticket_repo = ticket_repo
        self._message_repo = message_repo
        self._participant_repo = participant_repo
        self._authorization_service = authorization_service
        self._clock = clock
        self._uow = uow

    async def execute(self, request: UpdateTicketMessageCommand) -> UpdateTicketMessageResult:
        ticket = await self._ticket_repo.get_by_id(request.ticket_id)
        message = await self._message_repo.get_by_id(request.message_id)
        if message.ticket_id != ticket.id:
            raise PermissionDeniedError("Message does not belong to the specified ticket.")
        if not await self._authorization_service.has_permission(request.actor_id, PERMISSION_TICKET_MANAGE_ANY):
            await ensure_participant(self._participant_repo, ticket.id, request.actor_id)
            if message.sender_user_id != request.actor_id:
                raise PermissionDeniedError("Only the sender or an admin can edit a message.")
        now = await self._clock.now()
        message.edit(request.body, now)
        async with self._uow:
            await self._message_repo.update(message)
            await self._uow.commit()
        return UpdateTicketMessageResult(message_id=message.id)
