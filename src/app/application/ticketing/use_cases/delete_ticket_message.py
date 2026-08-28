from app.application.shared.exceptions import PermissionDeniedError
from app.application.shared.ports import IClock, IUnitOfWork
from app.application.shared.use_case import UseCase
from app.application.ticketing.access import ensure_party
from app.application.ticketing.dto import (
    DeleteTicketMessageCommand,
    DeleteTicketMessageResult,
)
from app.domain.ticketing.repositories import (
    ITicketMessageRepository,
    ITicketRepository,
)


class DeleteTicketMessageUseCase(UseCase[DeleteTicketMessageCommand, DeleteTicketMessageResult]):
    def __init__(
        self,
        ticket_repo: ITicketRepository,
        message_repo: ITicketMessageRepository,
        clock: IClock,
        uow: IUnitOfWork,
    ) -> None:
        self._ticket_repo = ticket_repo
        self._message_repo = message_repo
        self._clock = clock
        self._uow = uow

    async def execute(self, request: DeleteTicketMessageCommand) -> DeleteTicketMessageResult:
        ticket = await self._ticket_repo.get_by_id(request.ticket_id)
        message = await self._message_repo.get_by_id(request.message_id)
        if message.ticket_id != ticket.id:
            raise PermissionDeniedError("Message does not belong to the specified ticket.")
        await ensure_party(ticket, request.actor_id)
        now = await self._clock.now()
        message.soft_delete(now)
        async with self._uow:
            await self._message_repo.update(message)
            await self._uow.commit()
        return DeleteTicketMessageResult(message_id=message.id)
