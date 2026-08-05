from fastapi import APIRouter, Depends

from app.application.reporting.dto import ReportingQuery
from app.application.reporting.use_cases.get_customer_statistics import GetCustomerStatisticsUseCase
from app.application.reporting.use_cases.get_dashboard_statistics import GetDashboardStatisticsUseCase
from app.application.reporting.use_cases.get_freelancer_statistics import GetFreelancerStatisticsUseCase
from app.application.reporting.use_cases.get_project_statistics import GetProjectStatisticsUseCase
from app.application.reporting.use_cases.get_system_analytics import GetSystemAnalyticsUseCase
from app.application.reporting.use_cases.get_user_statistics import GetUserStatisticsUseCase
from app.presentation.api.v1.reporting.schemas import (
    CustomerStatisticsResponse,
    DashboardStatisticsResponse,
    FreelancerStatisticsResponse,
    ProjectStatisticsResponse,
    SystemAnalyticsResponse,
    UserStatisticsResponse,
)
from app.presentation.core.envelope import SuccessEnvelope
from app.presentation.core.providers import (
    get_get_customer_statistics_use_case,
    get_get_dashboard_statistics_use_case,
    get_get_freelancer_statistics_use_case,
    get_get_project_statistics_use_case,
    get_get_system_analytics_use_case,
    get_get_user_statistics_use_case,
)
from app.presentation.core.security import get_current_user

router = APIRouter(prefix="/reporting", tags=["Reporting"])


@router.get(
    "/dashboard",
    response_model=SuccessEnvelope[DashboardStatisticsResponse],
    operation_id="get_dashboard_statistics",
)
async def get_dashboard_statistics(
    current_user=Depends(get_current_user),
    use_case: GetDashboardStatisticsUseCase = Depends(get_get_dashboard_statistics_use_case),
) -> SuccessEnvelope[DashboardStatisticsResponse]:
    result = await use_case.execute(ReportingQuery(actor_id=current_user.user_id))
    return SuccessEnvelope(
        message="Dashboard statistics.",
        data=DashboardStatisticsResponse(
            total_users=result.total_users,
            active_projects=result.active_projects,
            total_freelancers=result.total_freelancers,
            total_revenue=result.total_revenue,
        ),
    )


@router.get(
    "/users",
    response_model=SuccessEnvelope[UserStatisticsResponse],
    operation_id="get_user_statistics",
)
async def get_user_statistics(
    current_user=Depends(get_current_user),
    use_case: GetUserStatisticsUseCase = Depends(get_get_user_statistics_use_case),
) -> SuccessEnvelope[UserStatisticsResponse]:
    result = await use_case.execute(ReportingQuery(actor_id=current_user.user_id))
    return SuccessEnvelope(
        message="User statistics.",
        data=UserStatisticsResponse(
            total_users=result.total_users,
            verified_users=result.verified_users,
            active_users=result.active_users,
        ),
    )


@router.get(
    "/projects",
    response_model=SuccessEnvelope[ProjectStatisticsResponse],
    operation_id="get_project_statistics",
)
async def get_project_statistics(
    current_user=Depends(get_current_user),
    use_case: GetProjectStatisticsUseCase = Depends(get_get_project_statistics_use_case),
) -> SuccessEnvelope[ProjectStatisticsResponse]:
    result = await use_case.execute(ReportingQuery(actor_id=current_user.user_id))
    return SuccessEnvelope(
        message="Project statistics.",
        data=ProjectStatisticsResponse(
            created=result.created,
            completed=result.completed,
            cancelled=result.cancelled,
        ),
    )


@router.get(
    "/freelancers",
    response_model=SuccessEnvelope[FreelancerStatisticsResponse],
    operation_id="get_freelancer_statistics",
)
async def get_freelancer_statistics(
    current_user=Depends(get_current_user),
    use_case: GetFreelancerStatisticsUseCase = Depends(get_get_freelancer_statistics_use_case),
) -> SuccessEnvelope[FreelancerStatisticsResponse]:
    result = await use_case.execute(ReportingQuery(actor_id=current_user.user_id))
    return SuccessEnvelope(
        message="Freelancer statistics.",
        data=FreelancerStatisticsResponse(
            total_freelancers=result.total_freelancers,
            approved_freelancers=result.approved_freelancers,
            pending_freelancers=result.pending_freelancers,
            average_rating=result.average_rating,
        ),
    )


@router.get(
    "/customers",
    response_model=SuccessEnvelope[CustomerStatisticsResponse],
    operation_id="get_customer_statistics",
)
async def get_customer_statistics(
    current_user=Depends(get_current_user),
    use_case: GetCustomerStatisticsUseCase = Depends(get_get_customer_statistics_use_case),
) -> SuccessEnvelope[CustomerStatisticsResponse]:
    result = await use_case.execute(ReportingQuery(actor_id=current_user.user_id))
    return SuccessEnvelope(
        message="Customer statistics.",
        data=CustomerStatisticsResponse(
            total_customers=result.total_customers,
            active_projects=result.active_projects,
            completed_projects=result.completed_projects,
        ),
    )


@router.get(
    "/system-analytics",
    response_model=SuccessEnvelope[SystemAnalyticsResponse],
    operation_id="get_system_analytics",
)
async def get_system_analytics(
    current_user=Depends(get_current_user),
    use_case: GetSystemAnalyticsUseCase = Depends(get_get_system_analytics_use_case),
) -> SuccessEnvelope[SystemAnalyticsResponse]:
    result = await use_case.execute(ReportingQuery(actor_id=current_user.user_id))
    return SuccessEnvelope(
        message="System analytics.",
        data=SystemAnalyticsResponse(
            dashboard=DashboardStatisticsResponse(
                total_users=result.dashboard.total_users,
                active_projects=result.dashboard.active_projects,
                total_freelancers=result.dashboard.total_freelancers,
                total_revenue=result.dashboard.total_revenue,
            ),
            users=UserStatisticsResponse(
                total_users=result.users.total_users,
                verified_users=result.users.verified_users,
                active_users=result.users.active_users,
            ),
            projects=ProjectStatisticsResponse(
                created=result.projects.created,
                completed=result.projects.completed,
                cancelled=result.projects.cancelled,
            ),
            freelancers=FreelancerStatisticsResponse(
                total_freelancers=result.freelancers.total_freelancers,
                approved_freelancers=result.freelancers.approved_freelancers,
                pending_freelancers=result.freelancers.pending_freelancers,
                average_rating=result.freelancers.average_rating,
            ),
            customers=CustomerStatisticsResponse(
                total_customers=result.customers.total_customers,
                active_projects=result.customers.active_projects,
                completed_projects=result.customers.completed_projects,
            ),
        ),
    )
