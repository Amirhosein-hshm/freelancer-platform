import pytest

from app.application.shared.exceptions import PermissionDeniedError
from app.application.ticketing.dto import CloseTicketCommand
from app.application.ticketing.permissions import PERMISSION_TICKET_CLOSE_OWN
from app.application.ticketing.use_cases.close_ticket import CloseTicketUseCase
from app.domain.shared.exceptions import InvalidStateTransitionError
from app.domain.ticketing.enums import TicketStatus


def build_close(authorization_service, ticket_repo, participant_repo, clock, uow) -> CloseTicketUseCase:
    return CloseTicketUseCase(
        authorization_service=authorization_service,
        ticket_repo=ticket_repo,
        participant_repo=participant_repo,
        clock=clock,
        uow=uow,
    )


class TestCloseTicketUseCase:
    async def test_close_sets_closed(
        self, authorization_service, ticket_repo, participant_repo, clock, uow, make_ticket
    ):
        await make_ticket(ticket_id="ticket-1")
        authorization_service.grant("user-1", PERMISSION_TICKET_CLOSE_OWN)
        use_case = build_close(authorization_service, ticket_repo, participant_repo, clock, uow)

        result = await use_case.execute(CloseTicketCommand(actor_id="user-1", ticket_id="ticket-1"))

        assert result.status == TicketStatus.CLOSED
        ticket = await ticket_repo.get_by_id("ticket-1")
        assert ticket.closed_by_user_id == "user-1"
        assert ticket.closed_at == await clock.now()
        assert ticket.is_closed() is True
        assert uow.committed is True

    async def test_cannot_close_twice(
        self, authorization_service, ticket_repo, participant_repo, clock, uow, make_ticket
    ):
        await make_ticket(ticket_id="ticket-1", status=TicketStatus.CLOSED)
        authorization_service.grant("user-1", PERMISSION_TICKET_CLOSE_OWN)
        use_case = build_close(authorization_service, ticket_repo, participant_repo, clock, uow)

        with pytest.raises(InvalidStateTransitionError):
            await use_case.execute(CloseTicketCommand(actor_id="user-1", ticket_id="ticket-1"))

    async def test_non_participant_raises(
        self, authorization_service, ticket_repo, participant_repo, clock, uow, make_ticket
    ):
        await make_ticket(ticket_id="ticket-1")
        use_case = build_close(authorization_service, ticket_repo, participant_repo, clock, uow)

        with pytest.raises(PermissionDeniedError):
            await use_case.execute(CloseTicketCommand(actor_id="intruder", ticket_id="ticket-1"))
