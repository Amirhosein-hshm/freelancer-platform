from app.application.ticketing.dto import CreateTicketCommand
from app.application.ticketing.use_cases.create_ticket import CreateTicketUseCase
from app.domain.ticketing.enums import TicketParticipantRole, TicketPriority, TicketStatus


def build_create(
    ticket_repo, participant_repo, ticket_code_generator, id_generator, clock, uow
) -> CreateTicketUseCase:
    return CreateTicketUseCase(
        ticket_repo=ticket_repo,
        participant_repo=participant_repo,
        ticket_code_generator=ticket_code_generator,
        id_generator=id_generator,
        clock=clock,
        uow=uow,
    )


class TestCreateTicketUseCase:
    async def test_create_ticket_adds_requester(
        self,
        ticket_repo,
        participant_repo,
        ticket_code_generator,
        id_generator,
        clock,
        uow,
    ):
        use_case = build_create(
            ticket_repo, participant_repo, ticket_code_generator, id_generator, clock, uow
        )

        result = await use_case.execute(
            CreateTicketCommand(
                actor_id="user-1",
                subject="Payment problem",
                related_project_id="project-1",
                priority=TicketPriority.HIGH,
            )
        )

        ticket = await ticket_repo.get_by_id(result.ticket_id)
        assert ticket.status == TicketStatus.OPEN
        assert ticket.priority == TicketPriority.HIGH
        assert ticket.related_project_id == "project-1"
        assert result.ticket_code.startswith("TCK-2026-")
        participants = await participant_repo.list_by_ticket(ticket.id)
        assert len(participants) == 1
        assert participants[0].user_id == "user-1"
        assert participants[0].participant_role == TicketParticipantRole.REQUESTER
        assert uow.committed is True

    async def test_default_priority_is_normal(
        self,
        ticket_repo,
        participant_repo,
        ticket_code_generator,
        id_generator,
        clock,
        uow,
    ):
        use_case = build_create(
            ticket_repo, participant_repo, ticket_code_generator, id_generator, clock, uow
        )

        result = await use_case.execute(
            CreateTicketCommand(actor_id="user-1", subject="Hello")
        )

        assert (await ticket_repo.get_by_id(result.ticket_id)).priority == TicketPriority.NORMAL
