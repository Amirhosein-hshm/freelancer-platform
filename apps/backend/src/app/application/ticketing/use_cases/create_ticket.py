from app.application.shared.ports import (
    IClock,
    IIdGenerator,
    ITicketCodeGenerator,
    IUnitOfWork,
)
from app.application.shared.use_case import UseCase
from app.application.ticketing.dto import CreateTicketCommand, CreateTicketResult
from app.domain.ticketing.entities import Ticket
from app.domain.ticketing.enums import TicketPriority, TicketStatus
from app.domain.ticketing.repositories import ITicketRepository
from app.domain.ticketing.services import RelationshipEligibilityService


async def _create_ticket(
    *,
    requester_user_id: str,
    target_user_id: str,
    submitted_by_user_id: str | None,
    subject: str,
    priority: TicketPriority,
    ticket_repo: ITicketRepository,
    ticket_code_generator: ITicketCodeGenerator,
    id_generator: IIdGenerator,
    clock: IClock,
    uow: IUnitOfWork,
    relationship_service: RelationshipEligibilityService,
) -> CreateTicketResult:
    await relationship_service.ensure_related(
        user_a=requester_user_id,
        user_b=target_user_id,
    )
    now = await clock.now()
    code_value = await ticket_code_generator.next_code(now.year)
    ticket = Ticket(
        id=await id_generator.new_id(),
        ticket_code=code_value,
        created_by_user_id=requester_user_id,
        target_user_id=target_user_id,
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
    async with uow:
        await ticket_repo.add(ticket)
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
        ticket_code_generator: ITicketCodeGenerator,
        id_generator: IIdGenerator,
        clock: IClock,
        uow: IUnitOfWork,
        relationship_service: RelationshipEligibilityService,
    ) -> None:
        self._ticket_repo = ticket_repo
        self._ticket_code_generator = ticket_code_generator
        self._id_generator = id_generator
        self._clock = clock
        self._uow = uow
        self._relationship_service = relationship_service

    async def execute(self, request: CreateTicketCommand) -> CreateTicketResult:
        return await _create_ticket(
            requester_user_id=request.actor_id,
            target_user_id=request.target_user_id,
            submitted_by_user_id=request.actor_id,
            subject=request.subject,
            priority=request.priority,
            ticket_repo=self._ticket_repo,
            ticket_code_generator=self._ticket_code_generator,
            id_generator=self._id_generator,
            clock=self._clock,
            uow=self._uow,
            relationship_service=self._relationship_service,
        )
