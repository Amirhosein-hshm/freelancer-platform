from app.domain.ticketing.entities import Ticket, TicketMessage
from app.domain.ticketing.enums import (
    TicketMessageType,
    TicketPriority,
    TicketStatus,
)


def to_domain_ticket(row: object) -> Ticket:
    return Ticket(
        id=row.id,
        created_at=row.created_at,
        ticket_code=row.ticket_code,
        created_by_user_id=row.created_by_user_id,
        target_user_id=row.target_user_id,
        subject=row.subject,
        status=TicketStatus(row.status),
        priority=TicketPriority(row.priority),
        closed_by_user_id=row.closed_by_user_id,
        closed_at=row.closed_at,
        last_message_at=row.last_message_at,
        deleted_at=row.deleted_at,
        submitted_by_user_id=row.submitted_by_user_id,
    )


def to_domain_ticket_message(row: object) -> TicketMessage:
    return TicketMessage(
        id=row.id,
        created_at=row.created_at,
        ticket_id=row.ticket_id,
        sender_user_id=row.sender_user_id,
        message_type=TicketMessageType(row.message_type),
        body=row.body,
        is_internal=row.is_internal,
        sent_at=row.sent_at,
        edited_at=row.edited_at,
        deleted_at=row.deleted_at,
        attachment_file_asset_ids=list(row.attachment_file_asset_ids),
    )
