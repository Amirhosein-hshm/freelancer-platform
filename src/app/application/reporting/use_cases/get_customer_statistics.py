from app.application.reporting.dto import ReportingQuery
from app.application.shared.authorization import IAuthorizationService
from app.application.shared.use_case import UseCase
from app.domain.reporting.read_models import CustomerStatistics
from app.domain.reporting.repositories import IReportingReadRepository


class GetCustomerStatisticsUseCase(UseCase[ReportingQuery, CustomerStatistics]):
    def __init__(
        self,
        authorization_service: IAuthorizationService,
        reporting_read_repo: IReportingReadRepository,
    ) -> None:
        self._authorization_service = authorization_service
        self._reporting_read_repo = reporting_read_repo

    def execute(self, request: ReportingQuery) -> CustomerStatistics:
        self._authorization_service.require_permission(request.actor_id, "reporting.read")
        return self._reporting_read_repo.get_customer_statistics()
