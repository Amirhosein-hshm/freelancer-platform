from enum import Enum


class FreelancerApprovalStatus(Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    SUSPENDED = "suspended"


class FreelancerLevelEnum(Enum):
    """Closed ladder of freelancer levels, in ascending order.

    Eligibility is hierarchical: a freelancer may apply to any project whose
    ``required_level`` is at or below their own level. There is no per-level
    configuration table — these three values are the whole model.
    """

    JUNIOR = "junior"
    MID_LEVEL = "mid_level"
    SENIOR = "senior"

    def rank(self) -> int:
        return _LEVEL_RANKS[self]


_LEVEL_RANKS: dict[FreelancerLevelEnum, int] = {
    FreelancerLevelEnum.JUNIOR: 1,
    FreelancerLevelEnum.MID_LEVEL: 2,
    FreelancerLevelEnum.SENIOR: 3,
}
