from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.project.entities import Project
from app.domain.project.enums import ProjectStatus, ProjectVisibility
from app.domain.project.exceptions import ProjectNotFoundError
from app.domain.project.repositories import IProjectRepository
from app.domain.project.value_objects import ProjectCode
from app.domain.shared.types import EntityId
from app.infrastructure.db.models.freelancer_models import FreelancerLevelModel
from app.infrastructure.db.models.project_models import ProjectModel
from app.infrastructure.repositories.project_mapping import to_domain_project

_OPEN_STATUSES = (
    ProjectStatus.PUBLISHED.value,
    ProjectStatus.COLLECTING_APPLICATIONS.value,
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
        row = await self._session.get(ProjectModel, project_id)
        if row is None:
            raise ProjectNotFoundError(f"Project {project_id} not found.")
        return to_domain_project(row)

    async def get_by_code(self, project_code: ProjectCode) -> Project:
        result = await self._session.execute(
            select(ProjectModel).where(ProjectModel.project_code == project_code.value)
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
        self, customer_user_id: EntityId, status: ProjectStatus | None = None
    ) -> list[Project]:
        stmt = select(ProjectModel).where(ProjectModel.customer_user_id == customer_user_id)
        if status is not None:
            stmt = stmt.where(ProjectModel.status == status.value)
        stmt = stmt.order_by(ProjectModel.created_at.desc())
        result = await self._session.execute(stmt)
        return [to_domain_project(row) for row in result.scalars().all()]

    async def list_available_for_freelancer(self, level_id: EntityId) -> list[Project]:
        level = await self._session.get(FreelancerLevelModel, level_id)
        if level is None or not level.is_active:
            return []
        conditions = [ProjectModel.visibility != ProjectVisibility.INVITE_ONLY.value]
        if not level.can_apply_public_projects:
            conditions.append(ProjectModel.visibility != ProjectVisibility.PUBLIC.value)
        if not level.can_apply_private_projects:
            conditions.append(ProjectModel.visibility != ProjectVisibility.PRIVATE.value)
        result = await self._session.execute(
            select(ProjectModel)
            .where(
                ProjectModel.status.in_(_OPEN_STATUSES),
                ProjectModel.deleted_at.is_(None),
                *conditions,
            )
            .order_by(ProjectModel.created_at.desc())
        )
        return [to_domain_project(row) for row in result.scalars().all()]

    async def list_by_supervisor(self, supervisor_user_id: EntityId) -> list[Project]:
        result = await self._session.execute(
            select(ProjectModel)
            .where(ProjectModel.assigned_supervisor_user_id == supervisor_user_id)
            .order_by(ProjectModel.created_at.desc())
        )
        return [to_domain_project(row) for row in result.scalars().all()]

    async def list_by_category(self, category_id: EntityId) -> list[Project]:
        result = await self._session.execute(
            select(ProjectModel)
            .where(
                ProjectModel.category_id == category_id,
                ProjectModel.status.in_(_OPEN_STATUSES),
            )
            .order_by(ProjectModel.created_at.desc())
        )
        return [to_domain_project(row) for row in result.scalars().all()]
