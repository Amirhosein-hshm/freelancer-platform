from datetime import UTC, datetime

import pytest

from app.application.shared.exceptions import PermissionDeniedError
from app.application.ticketing.dto import CreateTicketOnBehalfCommand
from app.application.ticketing.use_cases.admin_create_ticket_on_behalf import (
    AdminCreateTicketOnBehalfUseCase,
)
from app.domain.iam.entities import User
from app.domain.iam.enums import UserStatus
from app.domain.iam.exceptions import UserNotFoundError
from app.domain.iam.value_objects import Email, PasswordHash
from app.domain.ticketing.enums import TicketParticipantRole, TicketPriority, TicketStatus
from tests.fakes.fake_user_repository import FakeUserRepository

NOW = datetime(2026, 8, 2, tzinfo=UTC)


@pytest.fixture
def user_repo() -> FakeUserRepository:
    return FakeUserRepository()


def build_on_behalf(
    authorization_service, user_repo, ticket_repo, participant_repo, ticket_code_generator, id_generator, clock, uow
):
    return AdminCreateTicketOnBehalfUseCase(
        authorization_service=authorization_service,
        user_repo=user_repo,
        ticket_repo=ticket_repo,
        participant_repo=participant_repo,
        ticket_code_generator=ticket_code_generator,
        id_generator=id_generator,
        clock=clock,
        uow=uow,
    )


async def seed_user(user_repo, user_id: str = "customer-1") -> None:
    await user_repo.add(
        User(
            id=user_id,
            email=Email("user@example.com"),
            phone=None,
            password_hash=PasswordHash("hashed"),
            first_name="Jane",
            last_name="Dev",
            status=UserStatus.ACTIVE,
            created_at=NOW,
        )
    )


class TestAdminCreateTicketOnBehalfUseCase:
    async def test_admin_creates_ticket_for_target_user(
        self,
        authorization_service,
        user_repo,
        ticket_repo,
        participant_repo,
        ticket_code_generator,
        id_generator,
        clock,
        uow,
    ):
        authorization_service.grant("admin-1", "ticket.create_on_behalf")
        await seed_user(user_repo)
        use_case = build_on_behalf(
            authorization_service,
            user_repo,
            ticket_repo,
            participant_repo,
            ticket_code_generator,
            id_generator,
            clock,
            uow,
        )

        result = await use_case.execute(
            CreateTicketOnBehalfCommand(
                actor_id="admin-1",
                target_user_id="customer-1",
                subject="Payment problem",
                priority=TicketPriority.HIGH,
            )
        )

        ticket = await ticket_repo.get_by_id(result.ticket_id)
        assert ticket.status == TicketStatus.OPEN
        assert ticket.created_by_user_id == "customer-1"
        assert ticket.submitted_by_user_id == "admin-1"
        assert ticket.priority == TicketPriority.HIGH
        participants = await participant_repo.list_by_ticket(ticket.id)
        assert len(participants) == 1
        assert participants[0].user_id == "customer-1"
        assert participants[0].participant_role == TicketParticipantRole.REQUESTER
        assert uow.committed is True

    async def test_without_permission_raises(
        self,
        authorization_service,
        user_repo,
        ticket_repo,
        participant_repo,
        ticket_code_generator,
        id_generator,
        clock,
        uow,
    ):
        use_case = build_on_behalf(
            authorization_service,
            user_repo,
            ticket_repo,
            participant_repo,
            ticket_code_generator,
            id_generator,
            clock,
            uow,
        )

        with pytest.raises(PermissionDeniedError):
            await use_case.execute(
                CreateTicketOnBehalfCommand(
                    actor_id="customer-1",
                    target_user_id="customer-2",
                    subject="Payment problem",
                )
            )

    async def test_nonexistent_target_user_raises(
        self,
        authorization_service,
        user_repo,
        ticket_repo,
        participant_repo,
        ticket_code_generator,
        id_generator,
        clock,
        uow,
    ):
        authorization_service.grant("admin-1", "ticket.create_on_behalf")
        use_case = build_on_behalf(
            authorization_service,
            user_repo,
            ticket_repo,
            participant_repo,
            ticket_code_generator,
            id_generator,
            clock,
            uow,
        )

        with pytest.raises(UserNotFoundError):
            await use_case.execute(
                CreateTicketOnBehalfCommand(
                    actor_id="admin-1",
                    target_user_id="missing-user",
                    subject="Payment problem",
                )
            )

    async def test_self_service_and_on_behalf_share_persisted_state(
        self,
        authorization_service,
        user_repo,
        ticket_repo,
        participant_repo,
        ticket_code_generator,
        id_generator,
        clock,
        uow,
    ):
        authorization_service.grant("admin-1", "ticket.create_on_behalf")
        await seed_user(user_repo)
        use_case = build_on_behalf(
            authorization_service,
            user_repo,
            ticket_repo,
            participant_repo,
            ticket_code_generator,
            id_generator,
            clock,
            uow,
        )

        result = await use_case.execute(
            CreateTicketOnBehalfCommand(
                actor_id="admin-1",
                target_user_id="customer-1",
                subject="Payment problem",
            )
        )

        ticket = await ticket_repo.get_by_id(result.ticket_id)
        assert ticket.created_by_user_id == "customer-1"
        assert ticket.submitted_by_user_id == "admin-1"
        assert ticket.assigned_to_user_id is None
        assert ticket.status == TicketStatus.OPEN
