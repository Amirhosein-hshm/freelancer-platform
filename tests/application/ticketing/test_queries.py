import pytest

from app.application.ticketing.dto import (
    GetTicketMessagesQuery,
    GetUserTicketsQuery,
    SendMessageCommand,
)
from app.application.ticketing.permissions import PERMISSION_TICKET_READ_OWN
from app.application.ticketing.use_cases.get_ticket_messages import (
    GetTicketMessagesUseCase,
)
from app.application.ticketing.use_cases.get_user_tickets import GetUserTicketsUseCase
from app.application.ticketing.use_cases.send_message import SendMessageUseCase
from app.domain.ticketing.exceptions import NotTicketParticipantError


class TestGetUserTicketsUseCase:
    def test_lists_created_and_assigned(self, authorization_service, ticket_repo, make_ticket):
        make_ticket(ticket_id="ticket-1", created_by="user-1")
        make_ticket(ticket_id="ticket-2", created_by="user-2", assigned_to="user-1")
        make_ticket(ticket_id="ticket-3", created_by="user-2")
        authorization_service.grant("user-1", PERMISSION_TICKET_READ_OWN)
        use_case = GetUserTicketsUseCase(
            authorization_service=authorization_service, ticket_repo=ticket_repo
        )

        result = use_case.execute(
            GetUserTicketsQuery(actor_id="user-1", user_id="user-1")
        )

        assert [t.ticket_id for t in result.tickets] == ["ticket-1", "ticket-2"]
        assert result.tickets[0].status.value == "open"


class TestGetTicketMessagesUseCase:
    def test_participant_can_read_messages(
        self,
        ticket_repo,
        message_repo,
        participant_repo,
        id_generator,
        clock,
        uow,
        make_ticket,
    ):
        make_ticket(ticket_id="ticket-1")
        sender = SendMessageUseCase(
            ticket_repo=ticket_repo,
            message_repo=message_repo,
            participant_repo=participant_repo,
            id_generator=id_generator,
            clock=clock,
            uow=uow,
        )
        sender.execute(
            SendMessageCommand(actor_id="user-1", ticket_id="ticket-1", body="First")
        )
        sender.execute(
            SendMessageCommand(actor_id="user-1", ticket_id="ticket-1", body="Second")
        )
        use_case = GetTicketMessagesUseCase(
            ticket_repo=ticket_repo,
            message_repo=message_repo,
            participant_repo=participant_repo,
        )

        result = use_case.execute(
            GetTicketMessagesQuery(actor_id="user-1", ticket_id="ticket-1")
        )

        assert [m.body for m in result.messages] == ["First", "Second"]

    def test_non_participant_raises(
        self, ticket_repo, message_repo, participant_repo, make_ticket
    ):
        make_ticket(ticket_id="ticket-1")
        use_case = GetTicketMessagesUseCase(
            ticket_repo=ticket_repo,
            message_repo=message_repo,
            participant_repo=participant_repo,
        )

        with pytest.raises(NotTicketParticipantError):
            use_case.execute(
                GetTicketMessagesQuery(actor_id="intruder", ticket_id="ticket-1")
            )
