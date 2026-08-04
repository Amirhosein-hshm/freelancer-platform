from app.application.reporting.dto import ReportingQuery
from app.application.shared.authorization import IAuthorizationService
from app.application.shared.use_case import UseCase
from app.domain.reporting.read_models import SystemAnalytics
from app.domain.reporting.repositories import IReportingReadRepository


class GetSystemAnalyticsUseCase(UseCase[ReportingQuery, SystemAnalytics]):
    def __init__(
        self,
        authorization_service: IAuthorizationService,
        reporting_read_repo: IReportingReadRepository,
    ) -> None:
        self._authorization_service = authorization_service
        self._reporting_read_repo = reporting_read_repo

    async def execute(self, request: ReportingQuery) -> SystemAnalytics:
        await self._authorization_service.require_permission(request.actor_id, "reporting.read")
        return SystemAnalytics(
            dashboard=await self._reporting_read_repo.get_dashboard_statistics(),
            users=await self._reporting_read_repo.get_user_statistics(),
            projects=await self._reporting_read_repo.get_project_statistics(),
            freelancers=await self._reporting_read_repo.get_freelancer_statistics(),
            customers=await self._reporting_read_repo.get_customer_statistics(),
        )
