import pytest

from app.application.shared.exceptions import PermissionDeniedError
from app.application.ticketing.dto import AssignTicketCommand
from app.application.ticketing.permissions import PERMISSION_TICKET_ASSIGN
from app.application.ticketing.use_cases.assign_ticket import AssignTicketUseCase
from app.domain.ticketing.enums import TicketParticipantRole


def build_assign(authorization_service, ticket_repo, participant_repo, id_generator, clock, uow) -> AssignTicketUseCase:
    return AssignTicketUseCase(
        authorization_service=authorization_service,
        ticket_repo=ticket_repo,
        participant_repo=participant_repo,
        id_generator=id_generator,
        clock=clock,
        uow=uow,
    )


class TestAssignTicketUseCase:
    async def test_assign_adds_assignee_participant(
        self, authorization_service, ticket_repo, participant_repo, id_generator, clock, uow, make_ticket
    ):
        await make_ticket(ticket_id="ticket-1")
        authorization_service.grant("user-1", PERMISSION_TICKET_ASSIGN)
        use_case = build_assign(authorization_service, ticket_repo, participant_repo, id_generator, clock, uow)

        result = await use_case.execute(
            AssignTicketCommand(actor_id="user-1", ticket_id="ticket-1", assignee_user_id="agent-1")
        )

        assert result.assigned_to_user_id == "agent-1"
        assert (await ticket_repo.get_by_id("ticket-1")).assigned_to_user_id == "agent-1"
        assert await participant_repo.is_participant("ticket-1", "agent-1") is True
        roles = await participant_repo.list_by_ticket("ticket-1")
        assignee = [p for p in roles if p.user_id == "agent-1"][0]
        assert assignee.participant_role == TicketParticipantRole.ASSIGNEE
        assert uow.committed is True

    async def test_actor_without_assign_permission_raises(
        self, authorization_service, ticket_repo, participant_repo, id_generator, clock, uow, make_ticket
    ):
        await make_ticket(ticket_id="ticket-1")
        use_case = build_assign(authorization_service, ticket_repo, participant_repo, id_generator, clock, uow)

        with pytest.raises(PermissionDeniedError):
            await use_case.execute(
                AssignTicketCommand(actor_id="intruder", ticket_id="ticket-1", assignee_user_id="agent-1")
            )
