import pytest

from app.application.ticketing.dto import AssignTicketCommand
from app.application.ticketing.use_cases.assign_ticket import AssignTicketUseCase
from app.domain.ticketing.enums import TicketParticipantRole
from app.domain.ticketing.exceptions import NotTicketParticipantError


def build_assign(ticket_repo, participant_repo, id_generator, clock, uow) -> AssignTicketUseCase:
    return AssignTicketUseCase(
        ticket_repo=ticket_repo,
        participant_repo=participant_repo,
        id_generator=id_generator,
        clock=clock,
        uow=uow,
    )


class TestAssignTicketUseCase:
    def test_assign_adds_assignee_participant(
        self, ticket_repo, participant_repo, id_generator, clock, uow, make_ticket
    ):
        make_ticket(ticket_id="ticket-1")
        use_case = build_assign(ticket_repo, participant_repo, id_generator, clock, uow)

        result = use_case.execute(
            AssignTicketCommand(actor_id="user-1", ticket_id="ticket-1", assignee_user_id="agent-1")
        )

        assert result.assigned_to_user_id == "agent-1"
        assert ticket_repo.get_by_id("ticket-1").assigned_to_user_id == "agent-1"
        assert participant_repo.is_participant("ticket-1", "agent-1") is True
        roles = participant_repo.list_by_ticket("ticket-1")
        assignee = [p for p in roles if p.user_id == "agent-1"][0]
        assert assignee.participant_role == TicketParticipantRole.ASSIGNEE
        assert uow.committed is True

    def test_non_participant_actor_raises(
        self, ticket_repo, participant_repo, id_generator, clock, uow, make_ticket
    ):
        make_ticket(ticket_id="ticket-1")
        use_case = build_assign(ticket_repo, participant_repo, id_generator, clock, uow)

        with pytest.raises(NotTicketParticipantError):
            use_case.execute(
                AssignTicketCommand(actor_id="intruder", ticket_id="ticket-1", assignee_user_id="agent-1")
            )
