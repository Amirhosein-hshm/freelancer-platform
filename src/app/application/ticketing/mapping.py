from app.application.ticketing.dto import TicketMessageResult, TicketResult
from app.domain.ticketing.entities import Ticket, TicketMessage


def to_ticket_result(ticket: Ticket) -> TicketResult:
    return TicketResult(
        ticket_id=ticket.id,
        ticket_code=ticket.ticket_code,
        created_by_user_id=ticket.created_by_user_id,
        target_user_id=ticket.target_user_id,
        related_project_id=ticket.related_project_id,
        related_category_id=ticket.related_category_id,
        subject=ticket.subject,
        status=ticket.status,
        priority=ticket.priority,
        closed_at=ticket.closed_at,
        last_message_at=ticket.last_message_at,
    )


def to_message_result(message: TicketMessage) -> TicketMessageResult:
    return TicketMessageResult(
        message_id=message.id,
        ticket_id=message.ticket_id,
        sender_user_id=message.sender_user_id,
        message_type=message.message_type,
        body=message.body,
        is_internal=message.is_internal,
        sent_at=message.sent_at,
        attachment_file_asset_ids=list(message.attachment_file_asset_ids),
    )