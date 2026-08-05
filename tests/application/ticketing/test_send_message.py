import pytest

from app.application.ticketing.dto import SendMessageCommand
from app.application.ticketing.use_cases.send_message import SendMessageUseCase
from app.domain.ticketing.enums import TicketMessageType, TicketStatus
from app.domain.ticketing.exceptions import NotTicketParticipantError, TicketClosedError


def build_send(
    ticket_repo, message_repo, participant_repo, id_generator, clock, uow
) -> SendMessageUseCase:
    return SendMessageUseCase(
        ticket_repo=ticket_repo,
        message_repo=message_repo,
        participant_repo=participant_repo,
        id_generator=id_generator,
        clock=clock,
        uow=uow,
    )


class TestSendMessageUseCase:
    async def test_send_message_touches_last_message(
        self, ticket_repo, message_repo, participant_repo, id_generator, clock, uow, make_ticket
    ):
        await make_ticket(ticket_id="ticket-1")
        use_case = build_send(
            ticket_repo, message_repo, participant_repo, id_generator, clock, uow
        )

        result = await use_case.execute(
            SendMessageCommand(
                actor_id="user-1",
                ticket_id="ticket-1",
                body="Can you check this?",
            )
        )

        message = (await message_repo.list_by_ticket("ticket-1"))[0]
        assert message.sender_user_id == "user-1"
        assert message.message_type == TicketMessageType.TEXT
        assert message.body == "Can you check this?"
        assert (await ticket_repo.get_by_id("ticket-1")).last_message_at == await clock.now()
        assert result.message_id == message.id
        assert uow.committed is True

    async def test_closed_ticket_raises(
        self, ticket_repo, message_repo, participant_repo, id_generator, clock, uow, make_ticket
    ):
        await make_ticket(ticket_id="ticket-1", status=TicketStatus.CLOSED)
        use_case = build_send(
            ticket_repo, message_repo, participant_repo, id_generator, clock, uow
        )

        with pytest.raises(TicketClosedError):
            await use_case.execute(
                SendMessageCommand(actor_id="user-1", ticket_id="ticket-1", body="Hi")
            )

    async def test_non_participant_raises(
        self, ticket_repo, message_repo, participant_repo, id_generator, clock, uow, make_ticket
    ):
        await make_ticket(ticket_id="ticket-1")
        use_case = build_send(
            ticket_repo, message_repo, participant_repo, id_generator, clock, uow
        )

        with pytest.raises(NotTicketParticipantError):
            await use_case.execute(
                SendMessageCommand(actor_id="intruder", ticket_id="ticket-1", body="Hi")
            )
