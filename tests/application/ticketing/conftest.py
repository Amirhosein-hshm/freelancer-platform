from datetime import UTC, datetime

import pytest

from app.domain.ticketing.entities import Ticket, TicketParticipant
from app.domain.ticketing.enums import TicketParticipantRole, TicketPriority, TicketStatus
from tests.fakes.fake_ticket_code_generator import FakeTicketCodeGenerator
from tests.fakes.fake_ticket_message_repository import FakeTicketMessageRepository
from tests.fakes.fake_ticket_participant_repository import FakeTicketParticipantRepository
from tests.fakes.fake_ticket_repository import FakeTicketRepository

NOW = datetime(2026, 8, 2, tzinfo=UTC)


@pytest.fixture
def ticket_repo() -> FakeTicketRepository:
    return FakeTicketRepository()


@pytest.fixture
def message_repo() -> FakeTicketMessageRepository:
    return FakeTicketMessageRepository()


@pytest.fixture
def participant_repo() -> FakeTicketParticipantRepository:
    return FakeTicketParticipantRepository()


@pytest.fixture
def ticket_code_generator() -> FakeTicketCodeGenerator:
    return FakeTicketCodeGenerator()


@pytest.fixture
def make_ticket(
    ticket_repo: FakeTicketRepository,
    participant_repo: FakeTicketParticipantRepository,
):
    def _make(
        ticket_id: str = "ticket-1",
        created_by: str = "user-1",
        status: TicketStatus = TicketStatus.OPEN,
        assigned_to: str | None = None,
        **overrides: object,
    ) -> Ticket:
        fields: dict[str, object] = {
            "id": ticket_id,
            "ticket_code": "TCK-2026-001",
            "created_by_user_id": created_by,
            "assigned_to_user_id": assigned_to,
            "related_project_id": None,
            "related_category_id": None,
            "subject": "Payment problem",
            "status": status,
            "priority": TicketPriority.NORMAL,
            "closed_by_user_id": None,
            "closed_at": None,
            "last_message_at": None,
            "deleted_at": None,
            "created_at": NOW,
        }
        fields.update(overrides)
        ticket = Ticket(**fields)  # type: ignore[arg-type]
        ticket_repo.add(ticket)
        participant_repo.add(
            TicketParticipant(
                id=f"participant-{ticket_id}-{created_by}",
                ticket_id=ticket_id,
                user_id=created_by,
                participant_role=TicketParticipantRole.REQUESTER,
                joined_at=NOW,
                left_at=None,
                created_at=NOW,
            )
        )
        return ticket

    return _make
