from enum import Enum


class TicketStatus(Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    WAITING_CUSTOMER = "waiting_customer"
    WAITING_FREELANCER = "waiting_freelancer"
    WAITING_SUPERVISOR = "waiting_supervisor"
    CLOSED = "closed"
    ARCHIVED = "archived"


class TicketPriority(Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class TicketMessageType(Enum):
    TEXT = "text"
    FILE = "file"
    SYSTEM = "system"


class TicketParticipantRole(Enum):
    REQUESTER = "requester"
    ASSIGNEE = "assignee"
    WATCHER = "watcher"
    SUPERVISOR = "supervisor"
    ADMIN = "admin"
    CUSTOMER = "customer"
    FREELANCER = "freelancer"
