from abc import ABC, abstractmethod

from app.domain.reporting.read_models import (
    CustomerStatistics,
    DashboardStatistics,
    FreelancerStatistics,
    ProjectStatistics,
    UserStatistics,
)


class IReportingReadRepository(ABC):
    @abstractmethod
    def get_dashboard_statistics(self) -> DashboardStatistics: ...

    @abstractmethod
    def get_user_statistics(self) -> UserStatistics: ...

    @abstractmethod
    def get_project_statistics(self) -> ProjectStatistics: ...

    @abstractmethod
    def get_freelancer_statistics(self) -> FreelancerStatistics: ...

    @abstractmethod
    def get_customer_statistics(self) -> CustomerStatistics: ...
