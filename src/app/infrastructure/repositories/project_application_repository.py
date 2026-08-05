from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.project.entities import ProjectApplication
from app.domain.project.enums import ProjectApplicationStatus
from app.domain.project.exceptions import ApplicationNotFoundError
from app.domain.project.repositories import IProjectApplicationRepository
from app.domain.shared.types import EntityId
from app.infrastructure.db.models.project_models import ProjectApplicationModel
from app.infrastructure.repositories.project_mapping import to_domain_project_application

_INACTIVE_STATUSES = (
    ProjectApplicationStatus.WITHDRAWN.value,
    ProjectApplicationStatus.EXPIRED.value,
    ProjectApplicationStatus.REJECTED.value,
)


class SqlAlchemyProjectApplicationRepository(IProjectApplicationRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, application: ProjectApplication) -> None:
        self._session.add(
            ProjectApplicationModel(
                id=application.id,
                project_id=application.project_id,
                freelancer_profile_id=application.freelancer_profile_id,
                status=application.status.value,
                cover_letter=application.cover_letter,
                proposed_amount=application.proposed_amount,
                proposed_days=application.proposed_days,
                applied_at=application.applied_at,
                decided_by_user_id=application.decided_by_user_id,
                decided_at=application.decided_at,
                decision_note=application.decision_note,
                withdrawn_at=application.withdrawn_at,
                submitted_by_user_id=application.submitted_by_user_id,
            )
        )

    async def get_by_id(self, application_id: EntityId) -> ProjectApplication:
        row = await self._session.get(ProjectApplicationModel, application_id)
        if row is None:
            raise ApplicationNotFoundError(f"Application {application_id} not found.")
        return to_domain_project_application(row)

    async def find_by_project_and_freelancer(
        self, project_id: EntityId, freelancer_profile_id: EntityId
    ) -> ProjectApplication | None:
        result = await self._session.execute(
            select(ProjectApplicationModel).where(
                ProjectApplicationModel.project_id == project_id,
                ProjectApplicationModel.freelancer_profile_id == freelancer_profile_id,
            )
        )
        row = result.scalar_one_or_none()
        return to_domain_project_application(row) if row is not None else None

    async def list_by_project(self, project_id: EntityId) -> list[ProjectApplication]:
        result = await self._session.execute(
            select(ProjectApplicationModel)
            .where(ProjectApplicationModel.project_id == project_id)
            .order_by(ProjectApplicationModel.applied_at.desc())
        )
        return [to_domain_project_application(row) for row in result.scalars().all()]

    async def count_active_for_freelancer(self, freelancer_profile_id: EntityId) -> int:
        result = await self._session.execute(
            select(func.count(ProjectApplicationModel.id)).where(
                ProjectApplicationModel.freelancer_profile_id == freelancer_profile_id,
                ProjectApplicationModel.status.not_in(_INACTIVE_STATUSES),
            )
        )
        return int(result.scalar_one())

    async def update(self, application: ProjectApplication) -> None:
        row = await self._session.get(ProjectApplicationModel, application.id)
        if row is None:
            raise ApplicationNotFoundError(f"Application {application.id} not found.")
        row.status = application.status.value
        row.cover_letter = application.cover_letter
        row.proposed_amount = application.proposed_amount
        row.proposed_days = application.proposed_days
        row.decided_by_user_id = application.decided_by_user_id
        row.decided_at = application.decided_at
        row.decision_note = application.decision_note
        row.withdrawn_at = application.withdrawn_at
        row.submitted_by_user_id = application.submitted_by_user_id
