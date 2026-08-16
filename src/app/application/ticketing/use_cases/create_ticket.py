from app.application.shared.ports import (
    IClock,
    IIdGenerator,
    ITicketCodeGenerator,
    IUnitOfWork,
)
from app.application.shared.use_case import UseCase
from app.application.ticketing.dto import CreateTicketCommand, CreateTicketResult
from app.domain.ticketing.entities import Ticket, TicketParticipant
from app.domain.ticketing.enums import TicketParticipantRole, TicketPriority, TicketStatus
from app.domain.ticketing.repositories import (
    ITicketParticipantRepository,
    ITicketRepository,
)


async def _create_ticket(
    *,
    requester_user_id: str,
    submitted_by_user_id: str | None,
    related_project_id: str | None,
    related_category_id: str | None,
    subject: str,
    priority: TicketPriority,
    ticket_repo: ITicketRepository,
    participant_repo: ITicketParticipantRepository,
    ticket_code_generator: ITicketCodeGenerator,
    id_generator: IIdGenerator,
    clock: IClock,
    uow: IUnitOfWork,
) -> CreateTicketResult:
    now = await clock.now()
    code_value = await ticket_code_generator.next_code(now.year)
    ticket = Ticket(
        id=await id_generator.new_id(),
        ticket_code=code_value,
        created_by_user_id=requester_user_id,
        assigned_to_user_id=None,
        related_project_id=related_project_id,
        related_category_id=related_category_id,
        subject=subject,
        status=TicketStatus.OPEN,
        priority=priority,
        closed_by_user_id=None,
        closed_at=None,
        last_message_at=None,
        deleted_at=None,
        submitted_by_user_id=submitted_by_user_id,
        created_at=now,
    )
    requester = TicketParticipant(
        id=await id_generator.new_id(),
        ticket_id=ticket.id,
        user_id=requester_user_id,
        participant_role=TicketParticipantRole.REQUESTER,
        joined_at=now,
        left_at=None,
        created_at=now,
    )
    async with uow:
        await ticket_repo.add(ticket)
        await participant_repo.add(requester)
        await uow.commit()
    return CreateTicketResult(
        ticket_id=ticket.id,
        ticket_code=ticket.ticket_code,
        status=ticket.status,
    )


class CreateTicketUseCase(UseCase[CreateTicketCommand, CreateTicketResult]):
    def __init__(
        self,
        ticket_repo: ITicketRepository,
        participant_repo: ITicketParticipantRepository,
        ticket_code_generator: ITicketCodeGenerator,
        id_generator: IIdGenerator,
        clock: IClock,
        uow: IUnitOfWork,
    ) -> None:
        self._ticket_repo = ticket_repo
        self._participant_repo = participant_repo
        self._ticket_code_generator = ticket_code_generator
        self._id_generator = id_generator
        self._clock = clock
        self._uow = uow

    async def execute(self, request: CreateTicketCommand) -> CreateTicketResult:
        return await _create_ticket(
            requester_user_id=request.actor_id,
            submitted_by_user_id=request.actor_id,
            related_project_id=request.related_project_id,
            related_category_id=request.related_category_id,
            subject=request.subject,
            priority=request.priority,
            ticket_repo=self._ticket_repo,
            participant_repo=self._participant_repo,
            ticket_code_generator=self._ticket_code_generator,
            id_generator=self._id_generator,
            clock=self._clock,
            uow=self._uow,
        )
