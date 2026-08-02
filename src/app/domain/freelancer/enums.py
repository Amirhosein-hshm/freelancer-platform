from enum import Enum


class FreelancerApprovalStatus(Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    SUSPENDED = "suspended"


class FreelancerLevelAccessType(Enum):
    STANDARD = "standard"
    RESTRICTED = "restricted"
    PREMIUM = "premium"
