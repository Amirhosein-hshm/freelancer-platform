from app.application.shared.ports import (
    IClock,
    IIdGenerator,
    ITicketCodeGenerator,
    IUnitOfWork,
)
from app.application.shared.use_case import UseCase
from app.application.ticketing.dto import CreateTicketCommand, CreateTicketResult
from app.domain.ticketing.entities import Ticket, TicketParticipant
from app.domain.ticketing.enums import TicketParticipantRole, TicketStatus
from app.domain.ticketing.repositories import (
    ITicketParticipantRepository,
    ITicketRepository,
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

    def execute(self, request: CreateTicketCommand) -> CreateTicketResult:
        now = self._clock.now()
        code_value = self._ticket_code_generator.next_code(now.year)
        ticket = Ticket(
            id=self._id_generator.new_id(),
            ticket_code=code_value,
            created_by_user_id=request.actor_id,
            assigned_to_user_id=None,
            related_project_id=request.related_project_id,
            related_category_id=request.related_category_id,
            subject=request.subject,
            status=TicketStatus.OPEN,
            priority=request.priority,
            closed_by_user_id=None,
            closed_at=None,
            last_message_at=None,
            deleted_at=None,
            created_at=now,
        )
        requester = TicketParticipant(
            id=self._id_generator.new_id(),
            ticket_id=ticket.id,
            user_id=request.actor_id,
            participant_role=TicketParticipantRole.REQUESTER,
            joined_at=now,
            left_at=None,
            created_at=now,
        )
        with self._uow:
            self._ticket_repo.add(ticket)
            self._participant_repo.add(requester)
            self._uow.commit()
        return CreateTicketResult(
            ticket_id=ticket.id,
            ticket_code=ticket.ticket_code,
            status=ticket.status,
        )
