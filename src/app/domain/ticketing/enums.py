from enum import Enum


class TicketStatus(Enum):
    OPEN = "open"
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
