from decimal import Decimal

from pydantic import BaseModel


class DashboardStatisticsResponse(BaseModel):
    total_users: int
    active_projects: int
    total_freelancers: int
    total_revenue: Decimal


class UserStatisticsResponse(BaseModel):
    total_users: int
    verified_users: int
    active_users: int


class ProjectStatisticsResponse(BaseModel):
    created: int
    completed: int
    cancelled: int


class FreelancerStatisticsResponse(BaseModel):
    total_freelancers: int
    approved_freelancers: int
    pending_freelancers: int
    average_rating: Decimal | None


class CustomerStatisticsResponse(BaseModel):
    total_customers: int
    active_projects: int
    completed_projects: int


class SystemAnalyticsResponse(BaseModel):
    dashboard: DashboardStatisticsResponse
    users: UserStatisticsResponse
    projects: ProjectStatisticsResponse
    freelancers: FreelancerStatisticsResponse
    customers: CustomerStatisticsResponse
