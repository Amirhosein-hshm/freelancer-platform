from datetime import UTC, datetime

import pytest

from app.application.ticketing.dto import (
    DeleteTicketMessageCommand,
    UpdateTicketMessageCommand,
)
from app.application.ticketing.use_cases.delete_ticket_message import (
    DeleteTicketMessageUseCase,
)
from app.application.ticketing.use_cases.update_ticket_message import (
    UpdateTicketMessageUseCase,
)
from app.domain.shared.exceptions import InvalidStateTransitionError
from app.domain.ticketing.entities import TicketMessage
from app.domain.ticketing.enums import TicketMessageType
from app.domain.ticketing.exceptions import NotTicketParticipantError

NOW = datetime(2026, 8, 2, tzinfo=UTC)


class TestUpdateTicketMessageUseCase:
    async def test_sender_can_edit_own_message(
        self,
        authorization_service,
        ticket_repo,
        message_repo,
        participant_repo,
        clock,
        uow,
        make_ticket,
    ):
        await make_ticket(created_by="user-1")
        await message_repo.add(
            TicketMessage(
                id="message-1",
                ticket_id="ticket-1",
                sender_user_id="user-1",
                message_type=TicketMessageType.TEXT,
                body="hello",
                is_internal=False,
                sent_at=NOW,
                edited_at=None,
                deleted_at=None,
                attachment_file_asset_ids=[],
                created_at=NOW,
            )
        )
        use_case = UpdateTicketMessageUseCase(
            ticket_repo, message_repo, participant_repo, authorization_service, clock, uow
        )

        await use_case.execute(
            UpdateTicketMessageCommand(actor_id="user-1", ticket_id="ticket-1", message_id="message-1", body="updated")
        )

        message = await message_repo.get_by_id("message-1")
        assert message.body == "updated"
        assert message.edited_at is not None

    async def test_non_sender_cannot_edit(
        self,
        authorization_service,
        ticket_repo,
        message_repo,
        participant_repo,
        clock,
        uow,
        make_ticket,
    ):
        await make_ticket(created_by="user-1")
        await message_repo.add(
            TicketMessage(
                id="message-1",
                ticket_id="ticket-1",
                sender_user_id="user-1",
                message_type=TicketMessageType.TEXT,
                body="hello",
                is_internal=False,
                sent_at=NOW,
                edited_at=None,
                deleted_at=None,
                attachment_file_asset_ids=[],
                created_at=NOW,
            )
        )
        use_case = UpdateTicketMessageUseCase(
            ticket_repo, message_repo, participant_repo, authorization_service, clock, uow
        )

        with pytest.raises(NotTicketParticipantError):
            await use_case.execute(
                UpdateTicketMessageCommand(
                    actor_id="user-2", ticket_id="ticket-1", message_id="message-1", body="hacked"
                )
            )

    async def test_cannot_edit_deleted_message(
        self,
        authorization_service,
        ticket_repo,
        message_repo,
        participant_repo,
        clock,
        uow,
        make_ticket,
    ):
        await make_ticket(created_by="user-1")
        await message_repo.add(
            TicketMessage(
                id="message-1",
                ticket_id="ticket-1",
                sender_user_id="user-1",
                message_type=TicketMessageType.TEXT,
                body="hello",
                is_internal=False,
                sent_at=NOW,
                edited_at=None,
                deleted_at=NOW,
                attachment_file_asset_ids=[],
                created_at=NOW,
            )
        )
        use_case = UpdateTicketMessageUseCase(
            ticket_repo, message_repo, participant_repo, authorization_service, clock, uow
        )

        with pytest.raises(InvalidStateTransitionError):
            await use_case.execute(
                UpdateTicketMessageCommand(
                    actor_id="user-1", ticket_id="ticket-1", message_id="message-1", body="updated"
                )
            )


class TestDeleteTicketMessageUseCase:
    async def test_sender_can_soft_delete_message(
        self,
        authorization_service,
        ticket_repo,
        message_repo,
        participant_repo,
        clock,
        uow,
        make_ticket,
    ):
        await make_ticket(created_by="user-1")
        await message_repo.add(
            TicketMessage(
                id="message-1",
                ticket_id="ticket-1",
                sender_user_id="user-1",
                message_type=TicketMessageType.TEXT,
                body="hello",
                is_internal=False,
                sent_at=NOW,
                edited_at=None,
                deleted_at=None,
                attachment_file_asset_ids=[],
                created_at=NOW,
            )
        )
        use_case = DeleteTicketMessageUseCase(
            ticket_repo, message_repo, participant_repo, authorization_service, clock, uow
        )

        await use_case.execute(
            DeleteTicketMessageCommand(actor_id="user-1", ticket_id="ticket-1", message_id="message-1")
        )

        message = await message_repo.get_by_id("message-1")
        assert message.deleted_at is not None

    async def test_non_sender_cannot_delete(
        self,
        authorization_service,
        ticket_repo,
        message_repo,
        participant_repo,
        clock,
        uow,
        make_ticket,
    ):
        await make_ticket(created_by="user-1")
        await message_repo.add(
            TicketMessage(
                id="message-1",
                ticket_id="ticket-1",
                sender_user_id="user-1",
                message_type=TicketMessageType.TEXT,
                body="hello",
                is_internal=False,
                sent_at=NOW,
                edited_at=None,
                deleted_at=None,
                attachment_file_asset_ids=[],
                created_at=NOW,
            )
        )
        use_case = DeleteTicketMessageUseCase(
            ticket_repo, message_repo, participant_repo, authorization_service, clock, uow
        )

        with pytest.raises(NotTicketParticipantError):
            await use_case.execute(
                DeleteTicketMessageCommand(actor_id="user-2", ticket_id="ticket-1", message_id="message-1")
            )
