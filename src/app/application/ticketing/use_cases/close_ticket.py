from app.application.shared.ports import IClock, IUnitOfWork
from app.application.shared.use_case import UseCase
from app.application.ticketing.access import ensure_participant
from app.application.ticketing.dto import (
    CloseTicketCommand,
    CloseTicketResult,
)
from app.domain.ticketing.repositories import (
    ITicketParticipantRepository,
    ITicketRepository,
)


class CloseTicketUseCase(UseCase[CloseTicketCommand, CloseTicketResult]):
    def __init__(
        self,
        ticket_repo: ITicketRepository,
        participant_repo: ITicketParticipantRepository,
        clock: IClock,
        uow: IUnitOfWork,
    ) -> None:
        self._ticket_repo = ticket_repo
        self._participant_repo = participant_repo
        self._clock = clock
        self._uow = uow

    def execute(self, request: CloseTicketCommand) -> CloseTicketResult:
        ticket = self._ticket_repo.get_by_id(request.ticket_id)
        ensure_participant(self._participant_repo, ticket.id, request.actor_id)
        now = self._clock.now()
        with self._uow:
            ticket.close(request.actor_id, now)
            self._ticket_repo.update(ticket)
            self._uow.commit()
        return CloseTicketResult(ticket_id=ticket.id, status=ticket.status)
