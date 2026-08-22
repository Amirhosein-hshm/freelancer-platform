from datetime import datetime

from pydantic import BaseModel, Field

from app.domain.ticketing.enums import (
    TicketMessageType,
    TicketPriority,
    TicketStatus,
)


class CreateTicketRequest(BaseModel):
    target_user_id: str
    subject: str = Field(..., min_length=1)
    priority: TicketPriority = TicketPriority.NORMAL


class AdminCreateTicketRequest(BaseModel):
    requester_user_id: str
    target_user_id: str
    subject: str = Field(..., min_length=1)
    priority: TicketPriority = TicketPriority.NORMAL


class CreateTicketResponse(BaseModel):
    ticket_id: str
    ticket_code: str
    status: TicketStatus


class SendMessageRequest(BaseModel):
    body: str = Field(..., min_length=1)
    attachment_file_asset_ids: list[str] = Field(default_factory=list)


class SendMessageResponse(BaseModel):
    message_id: str
    ticket_id: str
    last_message_at: datetime


class TicketMessageResponse(BaseModel):
    message_id: str
    ticket_id: str
    sender_user_id: str
    message_type: TicketMessageType
    body: str | None
    is_internal: bool
    sent_at: datetime
    attachment_file_asset_ids: list[str]


class TicketResponse(BaseModel):
    ticket_id: str
    ticket_code: str
    created_by_user_id: str
    target_user_id: str
    subject: str
    status: TicketStatus
    priority: TicketPriority
    closed_at: datetime | None
    last_message_at: datetime | None


class CloseTicketResponse(BaseModel):
    ticket_id: str
    status: TicketStatus


class UpdateTicketRequest(BaseModel):
    subject: str | None = Field(None, min_length=1)
    priority: TicketPriority | None = None
    status: TicketStatus | None = None


class UpdateTicketMessageRequest(BaseModel):
    body: str = Field(..., min_length=1)
