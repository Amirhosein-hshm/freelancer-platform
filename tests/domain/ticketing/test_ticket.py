from datetime import UTC, datetime

import pytest

from app.domain.shared.exceptions import InvalidStateTransitionError
from app.domain.ticketing.entities import Ticket
from app.domain.ticketing.enums import TicketPriority, TicketStatus

NOW = datetime(2026, 8, 2, tzinfo=UTC)


def make_ticket(status: TicketStatus = TicketStatus.OPEN, **overrides: object) -> Ticket:
    fields: dict[str, object] = {
        "id": "ticket-1",
        "ticket_code": "TCK-2026-001",
        "created_by_user_id": "user-1",
        "target_user_id": "user-2",
        "subject": "Problem with payment",
        "status": status,
        "priority": TicketPriority.NORMAL,
        "closed_by_user_id": None,
        "closed_at": None,
        "last_message_at": None,
        "deleted_at": None,
        "created_at": NOW,
    }
    fields.update(overrides)
    return Ticket(**fields)  # type: ignore[arg-type]


class TestTicket:
    def test_target_is_party(self):
        ticket = make_ticket()
        assert ticket.is_party("user-2") is True

    def test_close_sets_status_and_timestamp(self):
        ticket = make_ticket()
        ticket.close("user-1", NOW)
        assert ticket.status == TicketStatus.CLOSED
        assert ticket.closed_by_user_id == "user-1"
        assert ticket.closed_at == NOW
        assert ticket.is_closed() is True

    def test_cannot_close_twice(self):
        ticket = make_ticket(status=TicketStatus.CLOSED)
        with pytest.raises(InvalidStateTransitionError):
            ticket.close("user-1", NOW)

    def test_touch_last_message(self):
        ticket = make_ticket()
        ticket.touch_last_message(NOW)
        assert ticket.last_message_at == NOW

    def test_archived_is_closed(self):
        ticket = make_ticket(status=TicketStatus.ARCHIVED)
        assert ticket.is_closed() is True

    def test_open_is_not_closed(self):
        ticket = make_ticket()
        assert ticket.is_closed() is False

    def test_identity_based_equality(self):
        assert make_ticket() == make_ticket()
        assert make_ticket() != make_ticket(id="ticket-2")
