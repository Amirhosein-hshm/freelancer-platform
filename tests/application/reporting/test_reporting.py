from decimal import Decimal

import pytest

from app.application.reporting.dto import ReportingQuery
from app.application.reporting.use_cases.get_customer_statistics import (
    GetCustomerStatisticsUseCase,
)
from app.application.reporting.use_cases.get_dashboard_statistics import (
    GetDashboardStatisticsUseCase,
)
from app.application.reporting.use_cases.get_freelancer_statistics import (
    GetFreelancerStatisticsUseCase,
)
from app.application.reporting.use_cases.get_project_statistics import (
    GetProjectStatisticsUseCase,
)
from app.application.reporting.use_cases.get_system_analytics import (
    GetSystemAnalyticsUseCase,
)
from app.application.reporting.use_cases.get_user_statistics import GetUserStatisticsUseCase
from app.application.shared.exceptions import PermissionDeniedError
from tests.fakes.fake_authorization_service import FakeAuthorizationService
from tests.fakes.fake_reporting_read_repository import FakeReportingReadRepository


def build_dashboard(auth, read_repo):
    return GetDashboardStatisticsUseCase(authorization_service=auth, reporting_read_repo=read_repo)


class TestReportingUseCases:
    def test_dashboard_statistics(self):
        auth = FakeAuthorizationService()
        auth.grant("admin-1", "reporting.read")
        read_repo = FakeReportingReadRepository()
        use_case = build_dashboard(auth, read_repo)

        result = use_case.execute(ReportingQuery(actor_id="admin-1"))

        assert result.total_users == 10
        assert result.total_revenue == Decimal("1200.00")

    def test_user_statistics(self):
        auth = FakeAuthorizationService()
        auth.grant("admin-1", "reporting.read")
        use_case = GetUserStatisticsUseCase(
            authorization_service=auth,
            reporting_read_repo=FakeReportingReadRepository(),
        )

        result = use_case.execute(ReportingQuery(actor_id="admin-1"))

        assert result.verified_users == 8

    def test_project_statistics(self):
        auth = FakeAuthorizationService()
        auth.grant("admin-1", "reporting.read")
        use_case = GetProjectStatisticsUseCase(
            authorization_service=auth,
            reporting_read_repo=FakeReportingReadRepository(),
        )

        result = use_case.execute(ReportingQuery(actor_id="admin-1"))

        assert result.completed == 5

    def test_freelancer_statistics(self):
        auth = FakeAuthorizationService()
        auth.grant("admin-1", "reporting.read")
        use_case = GetFreelancerStatisticsUseCase(
            authorization_service=auth,
            reporting_read_repo=FakeReportingReadRepository(),
        )

        result = use_case.execute(ReportingQuery(actor_id="admin-1"))

        assert result.approved_freelancers == 3
        assert result.average_rating == Decimal("4.5")

    def test_customer_statistics(self):
        auth = FakeAuthorizationService()
        auth.grant("admin-1", "reporting.read")
        use_case = GetCustomerStatisticsUseCase(
            authorization_service=auth,
            reporting_read_repo=FakeReportingReadRepository(),
        )

        result = use_case.execute(ReportingQuery(actor_id="admin-1"))

        assert result.total_customers == 6

    def test_system_analytics_composes_all_views(self):
        auth = FakeAuthorizationService()
        auth.grant("admin-1", "reporting.read")
        use_case = GetSystemAnalyticsUseCase(
            authorization_service=auth,
            reporting_read_repo=FakeReportingReadRepository(),
        )

        result = use_case.execute(ReportingQuery(actor_id="admin-1"))

        assert result.dashboard.total_freelancers == 4
        assert result.users.total_users == 10
        assert result.projects.created == 20
        assert result.freelancers.pending_freelancers == 1
        assert result.customers.active_projects == 3

    def test_missing_permission_raises(self):
        auth = FakeAuthorizationService()
        use_case = build_dashboard(auth, FakeReportingReadRepository())

        with pytest.raises(PermissionDeniedError):
            use_case.execute(ReportingQuery(actor_id="user-1"))
