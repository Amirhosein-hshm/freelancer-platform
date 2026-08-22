from dataclasses import dataclass, field
from datetime import datetime

from app.application.shared.pagination import DEFAULT_PAGE_SIZE
from app.domain.shared.types import EntityId
from app.domain.ticketing.enums import (
    TicketMessageType,
    TicketPriority,
    TicketStatus,
)


@dataclass(frozen=True)
class CreateTicketCommand:
    actor_id: EntityId
    target_user_id: EntityId
    subject: str
    priority: TicketPriority = TicketPriority.NORMAL


@dataclass(frozen=True)
class CreateTicketResult:
    ticket_id: EntityId
    ticket_code: str
    status: TicketStatus


@dataclass(frozen=True)
class CreateTicketOnBehalfCommand:
    actor_id: EntityId
    requester_user_id: EntityId
    target_user_id: EntityId
    subject: str
    priority: TicketPriority = TicketPriority.NORMAL


@dataclass(frozen=True)
class SendMessageCommand:
    actor_id: EntityId
    ticket_id: EntityId
    body: str
    attachment_file_asset_ids: list[EntityId] = field(default_factory=list)


@dataclass(frozen=True)
class SendMessageResult:
    message_id: EntityId
    ticket_id: EntityId
    last_message_at: datetime


@dataclass(frozen=True)
class GetTicketMessagesQuery:
    actor_id: EntityId
    ticket_id: EntityId
    page: int = 1
    page_size: int = DEFAULT_PAGE_SIZE


@dataclass(frozen=True)
class TicketMessageResult:
    message_id: EntityId
    ticket_id: EntityId
    sender_user_id: EntityId
    message_type: TicketMessageType
    body: str | None
    is_internal: bool
    sent_at: datetime
    attachment_file_asset_ids: list[EntityId]


@dataclass(frozen=True)
class GetTicketMessagesResult:
    messages: list[TicketMessageResult]
    total_items: int
    page: int
    page_size: int


@dataclass(frozen=True)
class GetUserTicketsQuery:
    actor_id: EntityId
    user_id: EntityId
    page: int = 1
    page_size: int = DEFAULT_PAGE_SIZE


@dataclass(frozen=True)
class TicketResult:
    ticket_id: EntityId
    ticket_code: str
    created_by_user_id: EntityId
    target_user_id: EntityId
    subject: str
    status: TicketStatus
    priority: TicketPriority
    closed_at: datetime | None
    last_message_at: datetime | None


@dataclass(frozen=True)
class GetUserTicketsResult:
    tickets: list[TicketResult]
    total_items: int
    page: int
    page_size: int


@dataclass(frozen=True)
class CloseTicketCommand:
    actor_id: EntityId
    ticket_id: EntityId


@dataclass(frozen=True)
class CloseTicketResult:
    ticket_id: EntityId
    status: TicketStatus


@dataclass(frozen=True)
class GetTicketQuery:
    actor_id: EntityId
    ticket_id: EntityId


@dataclass(frozen=True)
class GetTicketResult:
    ticket: TicketResult


@dataclass(frozen=True)
class UpdateTicketCommand:
    actor_id: EntityId
    ticket_id: EntityId
    subject: str | None = None
    priority: TicketPriority | None = None
    status: TicketStatus | None = None


@dataclass(frozen=True)
class UpdateTicketResult:
    ticket_id: EntityId
    status: TicketStatus


@dataclass(frozen=True)
class UpdateTicketMessageCommand:
    actor_id: EntityId
    ticket_id: EntityId
    message_id: EntityId
    body: str


@dataclass(frozen=True)
class UpdateTicketMessageResult:
    message_id: EntityId


@dataclass(frozen=True)
class DeleteTicketMessageCommand:
    actor_id: EntityId
    ticket_id: EntityId
    message_id: EntityId


@dataclass(frozen=True)
class DeleteTicketMessageResult:
    message_id: EntityId


@dataclass(frozen=True)
class ListRelatedUsersQuery:
    actor_id: EntityId
    user_id: EntityId
    page: int = 1
    page_size: int = DEFAULT_PAGE_SIZE


@dataclass(frozen=True)
class RelatedUserResult:
    user_id: EntityId
    email: str
    first_name: str
    last_name: str


@dataclass(frozen=True)
class ListRelatedUsersResult:
    users: list[RelatedUserResult]
    total_items: int
    page: int
    page_size: int
