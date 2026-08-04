from app.application.shared.ports import IClock, IIdGenerator, IUnitOfWork
from app.application.shared.use_case import UseCase
from app.application.ticketing.access import ensure_participant
from app.application.ticketing.dto import SendMessageCommand, SendMessageResult
from app.domain.ticketing.entities import TicketMessage
from app.domain.ticketing.enums import TicketMessageType
from app.domain.ticketing.exceptions import TicketClosedError
from app.domain.ticketing.repositories import (
    ITicketMessageRepository,
    ITicketParticipantRepository,
    ITicketRepository,
)


class SendMessageUseCase(UseCase[SendMessageCommand, SendMessageResult]):
    def __init__(
        self,
        ticket_repo: ITicketRepository,
        message_repo: ITicketMessageRepository,
        participant_repo: ITicketParticipantRepository,
        id_generator: IIdGenerator,
        clock: IClock,
        uow: IUnitOfWork,
    ) -> None:
        self._ticket_repo = ticket_repo
        self._message_repo = message_repo
        self._participant_repo = participant_repo
        self._id_generator = id_generator
        self._clock = clock
        self._uow = uow

    async def execute(self, request: SendMessageCommand) -> SendMessageResult:
        ticket = await self._ticket_repo.get_by_id(request.ticket_id)
        if ticket.is_closed():
            raise TicketClosedError(
                f"Ticket {ticket.id} is closed and accepts no new messages."
            )
        await ensure_participant(self._participant_repo, ticket.id, request.actor_id)
        now = await self._clock.now()
        message = TicketMessage(
            id=await self._id_generator.new_id(),
            ticket_id=ticket.id,
            sender_user_id=request.actor_id,
            message_type=TicketMessageType.TEXT,
            body=request.body,
            is_internal=False,
            sent_at=now,
            edited_at=None,
            deleted_at=None,
            attachment_file_asset_ids=list(request.attachment_file_asset_ids),
            created_at=now,
        )
        async with self._uow:
            await self._message_repo.add(message)
            ticket.touch_last_message(now)
            await self._ticket_repo.update(ticket)
            await self._uow.commit()
        return SendMessageResult(
            message_id=message.id,
            ticket_id=ticket.id,
            last_message_at=ticket.last_message_at or now,
        )
