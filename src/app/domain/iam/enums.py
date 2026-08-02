from enum import Enum


class UserStatus(Enum):
    PENDING = "pending"
    ACTIVE = "active"
    BLOCKED = "blocked"
    ARCHIVED = "archived"
