from decimal import Decimal

from app.domain.reporting.read_models import (
    CustomerStatistics,
    DashboardStatistics,
    FreelancerStatistics,
    ProjectStatistics,
    UserStatistics,
)
from app.domain.reporting.repositories import IReportingReadRepository


class FakeReportingReadRepository(IReportingReadRepository):
    async def __init__(self) -> None:
        self.dashboard = DashboardStatistics(
            total_users=10,
            active_projects=3,
            total_freelancers=4,
            total_revenue=Decimal("1200.00"),
        )
        self.users = UserStatistics(total_users=10, verified_users=8, active_users=7)
        self.projects = ProjectStatistics(created=20, completed=5, cancelled=2)
        self.freelancers = FreelancerStatistics(
            total_freelancers=4,
            approved_freelancers=3,
            pending_freelancers=1,
            average_rating=Decimal("4.5"),
        )
        self.customers = CustomerStatistics(
            total_customers=6, active_projects=3, completed_projects=5
        )

    async def get_dashboard_statistics(self) -> DashboardStatistics:
        return self.dashboard

    async def get_user_statistics(self) -> UserStatistics:
        return self.users

    async def get_project_statistics(self) -> ProjectStatistics:
        return self.projects

    async def get_freelancer_statistics(self) -> FreelancerStatistics:
        return self.freelancers

    async def get_customer_statistics(self) -> CustomerStatistics:
        return self.customers
