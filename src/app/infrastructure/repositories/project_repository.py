from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.freelancer.enums import FreelancerLevelEnum
from app.domain.project.entities import Project
from app.domain.project.enums import ProjectStatus, ProjectVisibility
from app.domain.project.exceptions import ProjectNotFoundError
from app.domain.project.repositories import IProjectRepository
from app.domain.project.value_objects import ProjectCode
from app.domain.shared.types import EntityId
from app.infrastructure.db.models.project_models import ProjectModel
from app.infrastructure.repositories.project_mapping import to_domain_project

_OPEN_STATUSES = (
    ProjectStatus.PUBLISHED.value,
    ProjectStatus.COLLECTING_APPLICATIONS.value,
)

_TERMINAL_STATUSES = (
    ProjectStatus.COMPLETED.value,
    ProjectStatus.CANCELLED.value,
    ProjectStatus.ARCHIVED.value,
)


class SqlAlchemyProjectRepository(IProjectRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, project: Project) -> None:
        self._session.add(
            ProjectModel(
                id=project.id,
                project_code=project.project_code.value,
                customer_user_id=project.customer_user_id,
                category_id=project.category_id,
                form_template_id=project.form_template_id,
                required_level=project.required_level.value if project.required_level else None,
                assigned_supervisor_user_id=project.assigned_supervisor_user_id,
                selected_application_id=project.selected_application_id,
                title=project.title,
                description=project.description,
                visibility=project.visibility.value,
                priority=project.priority.value,
                budget_type=project.budget.budget_type.value,
                fixed_amount=project.budget.fixed_amount,
                min_amount=project.budget.min_amount,
                max_amount=project.budget.max_amount,
                currency_code=project.budget.currency_code,
                status=project.status.value,
                application_deadline=project.application_deadline,
                start_at=project.start_at,
                due_at=project.due_at,
                completed_at=project.completed_at,
                cancelled_at=project.cancelled_at,
                locked_at=project.locked_at,
                deleted_at=project.deleted_at,
                created_by_user_id=project.created_by_user_id,
            )
        )

    async def get_by_id(self, project_id: EntityId) -> Project:
        result = await self._session.execute(
            select(ProjectModel).where(ProjectModel.id == project_id, ProjectModel.deleted_at.is_(None))
        )
        row = result.scalar_one_or_none()
        if row is None:
            raise ProjectNotFoundError(f"Project {project_id} not found.")
        return to_domain_project(row)

    async def get_by_code(self, project_code: ProjectCode) -> Project:
        result = await self._session.execute(
            select(ProjectModel).where(
                ProjectModel.project_code == project_code.value,
                ProjectModel.deleted_at.is_(None),
            )
        )
        row = result.scalar_one_or_none()
        if row is None:
            raise ProjectNotFoundError(f"Project with code {project_code.value} not found.")
        return to_domain_project(row)

    async def update(self, project: Project) -> None:
        row = await self._session.get(ProjectModel, project.id)
        if row is None:
            raise ProjectNotFoundError(f"Project {project.id} not found.")
        row.project_code = project.project_code.value
        row.customer_user_id = project.customer_user_id
        row.category_id = project.category_id
        row.form_template_id = project.form_template_id
        row.required_level = project.required_level.value if project.required_level else None
        row.assigned_supervisor_user_id = project.assigned_supervisor_user_id
        row.selected_application_id = project.selected_application_id
        row.title = project.title
        row.description = project.description
        row.visibility = project.visibility.value
        row.priority = project.priority.value
        row.budget_type = project.budget.budget_type.value
        row.fixed_amount = project.budget.fixed_amount
        row.min_amount = project.budget.min_amount
        row.max_amount = project.budget.max_amount
        row.currency_code = project.budget.currency_code
        row.status = project.status.value
        row.application_deadline = project.application_deadline
        row.start_at = project.start_at
        row.due_at = project.due_at
        row.completed_at = project.completed_at
        row.cancelled_at = project.cancelled_at
        row.locked_at = project.locked_at
        row.deleted_at = project.deleted_at
        row.created_by_user_id = project.created_by_user_id

    async def list_by_customer(
        self,
        customer_user_id: EntityId,
        status: ProjectStatus | None = None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[Project]:
        stmt = select(ProjectModel).where(
            ProjectModel.customer_user_id == customer_user_id,
            ProjectModel.deleted_at.is_(None),
        )
        if status is not None:
            stmt = stmt.where(ProjectModel.status == status.value)
        stmt = stmt.order_by(ProjectModel.created_at.desc())
        if limit is not None:
            stmt = stmt.limit(limit).offset(offset or 0)
        result = await self._session.execute(stmt)
        return [to_domain_project(row) for row in result.scalars().all()]

    async def count_by_customer(
        self, customer_user_id: EntityId, status: ProjectStatus | None = None
    ) -> int:
        stmt = select(func.count()).select_from(ProjectModel).where(
            ProjectModel.customer_user_id == customer_user_id,
            ProjectModel.deleted_at.is_(None),
        )
        if status is not None:
            stmt = stmt.where(ProjectModel.status == status.value)
        result = await self._session.execute(stmt)
        return result.scalar_one()

    async def list_available_for_freelancer(
        self,
        current_level: FreelancerLevelEnum | None,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[Project]:
        # Hierarchical level gate: projects that declare a required_level are only visible when
        # the freelancer's level ranks at or above it; level-less freelancers only see projects
        # that declare no requirement. Everything else (INVITE_ONLY, terminal statuses, deleted)
        # is excluded regardless of level.
        level_conditions = [ProjectModel.required_level.is_(None)]
        if current_level is not None:
            allowed = {
                level.value for level in FreelancerLevelEnum if level.rank() <= current_level.rank()
            }
            level_conditions.append(ProjectModel.required_level.in_(allowed))
        stmt = (
            select(ProjectModel)
            .where(
                ProjectModel.status.in_(_OPEN_STATUSES),
                ProjectModel.deleted_at.is_(None),
                ProjectModel.visibility != ProjectVisibility.INVITE_ONLY.value,
                or_(*level_conditions),
            )
            .order_by(ProjectModel.created_at.desc())
        )
        if limit is not None:
            stmt = stmt.limit(limit).offset(offset or 0)
        result = await self._session.execute(stmt)
        return [to_domain_project(row) for row in result.scalars().all()]

    async def count_available_for_freelancer(self, current_level: FreelancerLevelEnum | None) -> int:
        level_conditions = [ProjectModel.required_level.is_(None)]
        if current_level is not None:
            allowed = {
                level.value for level in FreelancerLevelEnum if level.rank() <= current_level.rank()
            }
            level_conditions.append(ProjectModel.required_level.in_(allowed))
        result = await self._session.execute(
            select(func.count())
            .select_from(ProjectModel)
            .where(
                ProjectModel.status.in_(_OPEN_STATUSES),
                ProjectModel.deleted_at.is_(None),
                ProjectModel.visibility != ProjectVisibility.INVITE_ONLY.value,
                or_(*level_conditions),
            )
        )
        return result.scalar_one()

    async def list_by_supervisor(
        self,
        supervisor_user_id: EntityId,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[Project]:
        stmt = (
            select(ProjectModel)
            .where(
                ProjectModel.assigned_supervisor_user_id == supervisor_user_id,
                ProjectModel.deleted_at.is_(None),
            )
            .order_by(ProjectModel.created_at.desc())
        )
        if limit is not None:
            stmt = stmt.limit(limit).offset(offset or 0)
        result = await self._session.execute(stmt)
        return [to_domain_project(row) for row in result.scalars().all()]

    async def count_by_supervisor(self, supervisor_user_id: EntityId) -> int:
        result = await self._session.execute(
            select(func.count())
            .select_from(ProjectModel)
            .where(
                ProjectModel.assigned_supervisor_user_id == supervisor_user_id,
                ProjectModel.deleted_at.is_(None),
            )
        )
        return result.scalar_one()

    async def list_by_category(
        self,
        category_id: EntityId,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[Project]:
        stmt = (
            select(ProjectModel)
            .where(
                ProjectModel.category_id == category_id,
                ProjectModel.status.in_(_OPEN_STATUSES),
                ProjectModel.deleted_at.is_(None),
            )
            .order_by(ProjectModel.created_at.desc())
        )
        if limit is not None:
            stmt = stmt.limit(limit).offset(offset or 0)
        result = await self._session.execute(stmt)
        return [to_domain_project(row) for row in result.scalars().all()]

    async def count_active_by_category(self, category_id: EntityId) -> int:
        result = await self._session.execute(
            select(func.count())
            .select_from(ProjectModel)
            .where(
                ProjectModel.category_id == category_id,
                ProjectModel.deleted_at.is_(None),
                ProjectModel.status.not_in(_TERMINAL_STATUSES),
            )
        )
        return result.scalar_one()

    async def count_open_by_category(self, category_id: EntityId) -> int:
        result = await self._session.execute(
            select(func.count())
            .select_from(ProjectModel)
            .where(
                ProjectModel.category_id == category_id,
                ProjectModel.status.in_(_OPEN_STATUSES),
                ProjectModel.deleted_at.is_(None),
            )
        )
        return result.scalar_one()

    async def count_active_by_form_template(self, form_template_id: EntityId) -> int:
        result = await self._session.execute(
            select(func.count())
            .select_from(ProjectModel)
            .where(
                ProjectModel.form_template_id == form_template_id,
                ProjectModel.deleted_at.is_(None),
                ProjectModel.status.not_in(_TERMINAL_STATUSES),
            )
        )
        return result.scalar_one()
