from datetime import UTC, datetime

import pytest

from app.application.ticketing.dto import (
    GetTicketQuery,
    ListTicketParticipantsQuery,
    UpdateTicketCommand,
)
from app.application.ticketing.use_cases.get_ticket import GetTicketUseCase
from app.application.ticketing.use_cases.list_ticket_participants import (
    ListTicketParticipantsUseCase,
)
from app.application.ticketing.use_cases.update_ticket import UpdateTicketUseCase
from app.domain.shared.exceptions import InvalidStateTransitionError
from app.domain.ticketing.entities import TicketParticipant
from app.domain.ticketing.enums import TicketParticipantRole, TicketPriority, TicketStatus
from app.domain.ticketing.exceptions import NotTicketParticipantError


class TestGetTicketUseCase:
    async def test_participant_can_read_ticket(
        self,
        authorization_service,
        ticket_repo,
        participant_repo,
        make_ticket,
    ):
        await make_ticket()
        use_case = GetTicketUseCase(ticket_repo, participant_repo, authorization_service)

        result = await use_case.execute(GetTicketQuery(actor_id="user-1", ticket_id="ticket-1"))

        assert result.ticket.ticket_id == "ticket-1"

    async def test_non_participant_denied(
        self,
        authorization_service,
        ticket_repo,
        participant_repo,
        make_ticket,
    ):
        await make_ticket()
        use_case = GetTicketUseCase(ticket_repo, participant_repo, authorization_service)

        with pytest.raises(NotTicketParticipantError):
            await use_case.execute(GetTicketQuery(actor_id="intruder", ticket_id="ticket-1"))


class TestUpdateTicketUseCase:
    async def test_owner_can_update_subject_and_priority(
        self,
        authorization_service,
        ticket_repo,
        clock,
        uow,
        make_ticket,
    ):
        await make_ticket()
        authorization_service.grant("user-1", "ticket.manage_own")
        use_case = UpdateTicketUseCase(ticket_repo, authorization_service, clock, uow)

        await use_case.execute(
            UpdateTicketCommand(
                actor_id="user-1",
                ticket_id="ticket-1",
                subject="Updated subject",
                priority=TicketPriority.HIGH,
            )
        )

        ticket = await ticket_repo.get_by_id("ticket-1")
        assert ticket.subject == "Updated subject"
        assert ticket.priority == TicketPriority.HIGH

    async def test_close_and_reopen_ticket(
        self,
        authorization_service,
        ticket_repo,
        clock,
        uow,
        make_ticket,
    ):
        await make_ticket()
        authorization_service.grant("user-1", "ticket.manage_own")
        use_case = UpdateTicketUseCase(ticket_repo, authorization_service, clock, uow)

        await use_case.execute(UpdateTicketCommand(actor_id="user-1", ticket_id="ticket-1", status=TicketStatus.CLOSED))
        ticket = await ticket_repo.get_by_id("ticket-1")
        assert ticket.status == TicketStatus.CLOSED

        await use_case.execute(UpdateTicketCommand(actor_id="user-1", ticket_id="ticket-1", status=TicketStatus.OPEN))
        ticket = await ticket_repo.get_by_id("ticket-1")
        assert ticket.status == TicketStatus.OPEN

    async def test_archived_ticket_cannot_be_modified(
        self,
        authorization_service,
        ticket_repo,
        clock,
        uow,
        make_ticket,
    ):
        await make_ticket()
        authorization_service.grant("user-1", "ticket.manage_own")
        use_case = UpdateTicketUseCase(ticket_repo, authorization_service, clock, uow)
        await use_case.execute(
            UpdateTicketCommand(actor_id="user-1", ticket_id="ticket-1", status=TicketStatus.ARCHIVED)
        )

        with pytest.raises(InvalidStateTransitionError):
            await use_case.execute(UpdateTicketCommand(actor_id="user-1", ticket_id="ticket-1", subject="Nope"))


class TestListTicketParticipantsUseCase:
    async def test_lists_participants(
        self,
        authorization_service,
        ticket_repo,
        participant_repo,
        make_ticket,
    ):
        await make_ticket()
        await participant_repo.add(
            TicketParticipant(
                id="participant-2",
                ticket_id="ticket-1",
                user_id="user-2",
                participant_role=TicketParticipantRole.WATCHER,
                joined_at=datetime.now(UTC),
                left_at=None,
                created_at=datetime.now(UTC),
            )
        )
        use_case = ListTicketParticipantsUseCase(ticket_repo, participant_repo, authorization_service)

        result = await use_case.execute(ListTicketParticipantsQuery(actor_id="user-1", ticket_id="ticket-1"))

        assert len(result.participants) == 2
