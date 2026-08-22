from dataclasses import dataclass
from datetime import datetime

from app.domain.shared.entity import AggregateRoot, Entity
from app.domain.shared.exceptions import InvalidStateTransitionError
from app.domain.shared.types import EntityId
from app.domain.ticketing.enums import (
    TicketMessageType,
    TicketPriority,
    TicketStatus,
)

_CLOSED_STATUSES = (TicketStatus.CLOSED, TicketStatus.ARCHIVED)


@dataclass(eq=False)
class Ticket(AggregateRoot):
    ticket_code: str
    created_by_user_id: EntityId
    target_user_id: EntityId
    subject: str
    status: TicketStatus
    priority: TicketPriority
    closed_by_user_id: EntityId | None
    closed_at: datetime | None
    last_message_at: datetime | None
    deleted_at: datetime | None
    submitted_by_user_id: EntityId | None = None

    def is_party(self, user_id: EntityId) -> bool:
        return user_id in (self.created_by_user_id, self.target_user_id)

    def close(self, by_user_id: EntityId, at: datetime) -> None:
        if self.is_closed():
            raise InvalidStateTransitionError(f"Ticket {self.id} is already '{self.status.value}'.")
        self.status = TicketStatus.CLOSED
        self.closed_by_user_id = by_user_id
        self.closed_at = at

    def reopen(self) -> None:
        if self.status != TicketStatus.CLOSED:
            raise InvalidStateTransitionError(
                f"Ticket {self.id} must be closed to reopen; current status is '{self.status.value}'."
            )
        self.status = TicketStatus.OPEN
        self.closed_by_user_id = None
        self.closed_at = None

    def archive(self, by_user_id: EntityId, at: datetime) -> None:
        if self.status == TicketStatus.ARCHIVED:
            raise InvalidStateTransitionError(f"Ticket {self.id} is already archived.")
        self.status = TicketStatus.ARCHIVED
        self.closed_by_user_id = by_user_id
        self.closed_at = at

    def set_priority(self, priority: TicketPriority) -> None:
        if self.status == TicketStatus.ARCHIVED:
            raise InvalidStateTransitionError(f"Ticket {self.id} is archived and cannot be modified.")
        self.priority = priority

    def update_subject(self, subject: str) -> None:
        if self.status == TicketStatus.ARCHIVED:
            raise InvalidStateTransitionError(f"Ticket {self.id} is archived and cannot be modified.")
        self.subject = subject

    def touch_last_message(self, at: datetime) -> None:
        self.last_message_at = at

    def is_closed(self) -> bool:
        return self.status in _CLOSED_STATUSES


@dataclass(eq=False)
class TicketMessage(Entity):
    ticket_id: EntityId
    sender_user_id: EntityId
    message_type: TicketMessageType
    body: str | None
    is_internal: bool
    sent_at: datetime
    edited_at: datetime | None
    deleted_at: datetime | None
    attachment_file_asset_ids: list[EntityId]

    def edit(self, body: str, at: datetime) -> None:
        if self.deleted_at is not None:
            raise InvalidStateTransitionError("Cannot edit a deleted message.")
        self.body = body
        self.edited_at = at

    def soft_delete(self, at: datetime) -> None:
        if self.deleted_at is not None:
            raise InvalidStateTransitionError("Message is already deleted.")
        self.deleted_at = at
