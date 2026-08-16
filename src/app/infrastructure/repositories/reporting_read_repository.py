from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.reporting.read_models import (
    CustomerStatistics,
    DashboardStatistics,
    FreelancerStatistics,
    ProjectStatistics,
    UserStatistics,
)
from app.domain.reporting.repositories import IReportingReadRepository
from app.infrastructure.db.models.feedback_models import RatingModel
from app.infrastructure.db.models.freelancer_models import FreelancerProfileModel
from app.infrastructure.db.models.iam_models import RoleModel, UserModel, UserRoleModel
from app.infrastructure.db.models.project_models import ProjectModel

_ACTIVE_PROJECT_STATUSES = (
    "published",
    "collecting_applications",
    "assigned",
    "in_progress",
    "delivery_submitted",
    "under_supervisor_review",
    "revision_requested",
    "awaiting_customer_review",
)

_APPROVED_FREELANCER_STATUS = "approved"
_PENDING_FREELANCER_STATUS = "pending"
_COMPLETED_PROJECT_STATUS = "completed"
_CANCELLED_PROJECT_STATUS = "cancelled"
_CUSTOMER_ROLE_KEY = "customer"


class SqlAlchemyReportingReadRepository(IReportingReadRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_dashboard_statistics(self) -> DashboardStatistics:
        total_users = await self._count_users()
        active_projects = await self._count_active_projects()
        total_freelancers = await self._count_freelancers()
        total_revenue = await self._sum_total_revenue()
        return DashboardStatistics(
            total_users=total_users,
            active_projects=active_projects,
            total_freelancers=total_freelancers,
            total_revenue=total_revenue,
        )

    async def get_user_statistics(self) -> UserStatistics:
        total_users = await self._count_users()
        verified_users = await self._count_verified_users()
        active_users = await self._count_active_users()
        return UserStatistics(
            total_users=total_users,
            verified_users=verified_users,
            active_users=active_users,
        )

    async def get_project_statistics(self) -> ProjectStatistics:
        created = await self._count_projects()
        completed = await self._count_projects_with_status(_COMPLETED_PROJECT_STATUS)
        cancelled = await self._count_projects_with_status(_CANCELLED_PROJECT_STATUS)
        return ProjectStatistics(
            created=created,
            completed=completed,
            cancelled=cancelled,
        )

    async def get_freelancer_statistics(self) -> FreelancerStatistics:
        total = await self._count_freelancers()
        approved = await self._count_freelancers_with_status(_APPROVED_FREELANCER_STATUS)
        pending = await self._count_freelancers_with_status(_PENDING_FREELANCER_STATUS)
        average_rating = await self._average_rating()
        return FreelancerStatistics(
            total_freelancers=total,
            approved_freelancers=approved,
            pending_freelancers=pending,
            average_rating=average_rating,
        )

    async def get_customer_statistics(self) -> CustomerStatistics:
        total_customers = await self._count_customers()
        active_projects = await self._count_active_projects()
        completed_projects = await self._count_projects_with_status(_COMPLETED_PROJECT_STATUS)
        return CustomerStatistics(
            total_customers=total_customers,
            active_projects=active_projects,
            completed_projects=completed_projects,
        )

    async def _count_users(self) -> int:
        stmt = select(func.count()).select_from(UserModel).where(UserModel.deleted_at.is_(None))
        return int((await self._session.execute(stmt)).scalar_one())

    async def _count_verified_users(self) -> int:
        stmt = (
            select(func.count())
            .select_from(UserModel)
            .where(
                UserModel.deleted_at.is_(None),
                UserModel.email_verified_at.is_not(None),
            )
        )
        return int((await self._session.execute(stmt)).scalar_one())

    async def _count_active_users(self) -> int:
        stmt = (
            select(func.count())
            .select_from(UserModel)
            .where(UserModel.deleted_at.is_(None), UserModel.status == "active")
        )
        return int((await self._session.execute(stmt)).scalar_one())

    async def _count_customers(self) -> int:
        stmt = (
            select(func.count(func.distinct(UserRoleModel.user_id)))
            .join(RoleModel, UserRoleModel.role_id == RoleModel.id)
            .join(UserModel, UserRoleModel.user_id == UserModel.id)
            .where(
                UserRoleModel.is_active.is_(True),
                UserRoleModel.revoked_at.is_(None),
                RoleModel.role_key == _CUSTOMER_ROLE_KEY,
                UserModel.deleted_at.is_(None),
            )
        )
        return int((await self._session.execute(stmt)).scalar_one())

    async def _count_projects(self) -> int:
        stmt = select(func.count()).select_from(ProjectModel).where(ProjectModel.deleted_at.is_(None))
        return int((await self._session.execute(stmt)).scalar_one())

    async def _count_projects_with_status(self, status: str) -> int:
        stmt = (
            select(func.count())
            .select_from(ProjectModel)
            .where(
                ProjectModel.deleted_at.is_(None),
                ProjectModel.status == status,
            )
        )
        return int((await self._session.execute(stmt)).scalar_one())

    async def _count_active_projects(self) -> int:
        stmt = (
            select(func.count())
            .select_from(ProjectModel)
            .where(
                ProjectModel.deleted_at.is_(None),
                ProjectModel.status.in_(_ACTIVE_PROJECT_STATUSES),
            )
        )
        return int((await self._session.execute(stmt)).scalar_one())

    async def _sum_total_revenue(self) -> Decimal:
        revenue_expr = func.coalesce(
            ProjectModel.fixed_amount,
            ProjectModel.max_amount,
            0,
        )
        stmt = (
            select(func.coalesce(func.sum(revenue_expr), 0))
            .select_from(ProjectModel)
            .where(
                ProjectModel.deleted_at.is_(None),
                ProjectModel.status == _COMPLETED_PROJECT_STATUS,
            )
        )
        return Decimal((await self._session.execute(stmt)).scalar_one())

    async def _count_freelancers(self) -> int:
        stmt = (
            select(func.count()).select_from(FreelancerProfileModel).where(FreelancerProfileModel.deleted_at.is_(None))
        )
        return int((await self._session.execute(stmt)).scalar_one())

    async def _count_freelancers_with_status(self, status: str) -> int:
        stmt = (
            select(func.count())
            .select_from(FreelancerProfileModel)
            .where(
                FreelancerProfileModel.deleted_at.is_(None),
                FreelancerProfileModel.approval_status == status,
            )
        )
        return int((await self._session.execute(stmt)).scalar_one())

    async def _average_rating(self) -> Decimal | None:
        stmt = select(func.avg(RatingModel.score))
        result = await self._session.execute(stmt)
        value = result.scalar_one()
        if value is None:
            return None
        return Decimal(value)
