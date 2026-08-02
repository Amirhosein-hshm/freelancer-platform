from enum import Enum


class ProjectVisibility(Enum):
    PUBLIC = "public"
    PRIVATE = "private"
    INVITE_ONLY = "invite_only"


class ProjectPriority(Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


class BudgetType(Enum):
    FIXED = "fixed"
    RANGE = "range"
    HOURLY = "hourly"
    NEGOTIABLE = "negotiable"


class ProjectStatus(Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    COLLECTING_APPLICATIONS = "collecting_applications"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    DELIVERY_SUBMITTED = "delivery_submitted"
    UNDER_SUPERVISOR_REVIEW = "under_supervisor_review"
    REVISION_REQUESTED = "revision_requested"
    AWAITING_CUSTOMER_REVIEW = "awaiting_customer_review"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    REJECTED = "rejected"
    ARCHIVED = "archived"


class ProjectApplicationStatus(Enum):
    APPLIED = "applied"
    SHORTLISTED = "shortlisted"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"
    EXPIRED = "expired"


class DeliveryStatus(Enum):
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    REVISED = "revised"
    SUPERSEDED = "superseded"


class RevisionRequestStatus(Enum):
    OPEN = "open"
    APPROVED = "approved"
    REJECTED = "rejected"
    CLOSED = "closed"
    CANCELLED = "cancelled"
