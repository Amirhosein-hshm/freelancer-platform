from datetime import datetime

from pydantic import BaseModel, Field

from app.domain.ticketing.enums import TicketMessageType, TicketPriority, TicketStatus


class CreateTicketRequest(BaseModel):
    subject: str = Field(..., min_length=1)
    related_project_id: str | None = None
    related_category_id: str | None = None
    priority: TicketPriority = TicketPriority.NORMAL


class AdminCreateTicketRequest(BaseModel):
    target_user_id: str
    subject: str = Field(..., min_length=1)
    related_project_id: str | None = None
    related_category_id: str | None = None
    priority: TicketPriority = TicketPriority.NORMAL


class CreateTicketResponse(BaseModel):
    ticket_id: str
    ticket_code: str
    status: TicketStatus


class AssignTicketRequest(BaseModel):
    assignee_user_id: str


class AssignTicketResponse(BaseModel):
    ticket_id: str
    assigned_to_user_id: str


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
    assigned_to_user_id: str | None
    related_project_id: str | None
    related_category_id: str | None
    subject: str
    status: TicketStatus
    priority: TicketPriority
    closed_at: datetime | None
    last_message_at: datetime | None


class CloseTicketResponse(BaseModel):
    ticket_id: str
    status: TicketStatus
