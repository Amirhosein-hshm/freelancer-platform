from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class DashboardStatistics:
    total_users: int
    active_projects: int
    total_freelancers: int
    total_revenue: Decimal


@dataclass(frozen=True)
class ProjectStatistics:
    created: int
    completed: int
    cancelled: int


@dataclass(frozen=True)
class UserStatistics:
    total_users: int
    verified_users: int
    active_users: int


@dataclass(frozen=True)
class FreelancerStatistics:
    total_freelancers: int
    approved_freelancers: int
    pending_freelancers: int
    average_rating: Decimal | None


@dataclass(frozen=True)
class CustomerStatistics:
    total_customers: int
    active_projects: int
    completed_projects: int


@dataclass(frozen=True)
class SystemAnalytics:
    dashboard: DashboardStatistics
    users: UserStatistics
    projects: ProjectStatistics
    freelancers: FreelancerStatistics
    customers: CustomerStatistics
