import pytest

from app.application.ticketing.dto import CloseTicketCommand
from app.application.ticketing.use_cases.close_ticket import CloseTicketUseCase
from app.domain.shared.exceptions import InvalidStateTransitionError
from app.domain.ticketing.enums import TicketStatus
from app.domain.ticketing.exceptions import NotTicketParticipantError


def build_close(ticket_repo, participant_repo, clock, uow) -> CloseTicketUseCase:
    return CloseTicketUseCase(
        ticket_repo=ticket_repo,
        participant_repo=participant_repo,
        clock=clock,
        uow=uow,
    )


class TestCloseTicketUseCase:
    def test_close_sets_closed(self, ticket_repo, participant_repo, clock, uow, make_ticket):
        make_ticket(ticket_id="ticket-1")
        use_case = build_close(ticket_repo, participant_repo, clock, uow)

        result = use_case.execute(
            CloseTicketCommand(actor_id="user-1", ticket_id="ticket-1")
        )

        assert result.status == TicketStatus.CLOSED
        ticket = ticket_repo.get_by_id("ticket-1")
        assert ticket.closed_by_user_id == "user-1"
        assert ticket.closed_at == clock.now()
        assert ticket.is_closed() is True
        assert uow.committed is True

    def test_cannot_close_twice(self, ticket_repo, participant_repo, clock, uow, make_ticket):
        make_ticket(ticket_id="ticket-1", status=TicketStatus.CLOSED)
        use_case = build_close(ticket_repo, participant_repo, clock, uow)

        with pytest.raises(InvalidStateTransitionError):
            use_case.execute(
                CloseTicketCommand(actor_id="user-1", ticket_id="ticket-1")
            )

    def test_non_participant_raises(self, ticket_repo, participant_repo, clock, uow, make_ticket):
        make_ticket(ticket_id="ticket-1")
        use_case = build_close(ticket_repo, participant_repo, clock, uow)

        with pytest.raises(NotTicketParticipantError):
            use_case.execute(
                CloseTicketCommand(actor_id="intruder", ticket_id="ticket-1")
            )
