from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.project.entities import ProjectStatusHistory
from app.domain.project.repositories import IProjectStatusHistoryRepository
from app.domain.shared.types import EntityId
from app.infrastructure.db.models.project_models import ProjectStatusHistoryModel
from app.infrastructure.repositories.project_mapping import to_domain_project_status_history


class SqlAlchemyProjectStatusHistoryRepository(IProjectStatusHistoryRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, history: ProjectStatusHistory) -> None:
        self._session.add(
            ProjectStatusHistoryModel(
                id=history.id,
                project_id=history.project_id,
                from_status=history.from_status.value if history.from_status else None,
                to_status=history.to_status.value,
                changed_by_user_id=history.changed_by_user_id,
                reason=history.reason,
                changed_at=history.changed_at,
            )
        )

    async def list_by_project(
        self,
        project_id: EntityId,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[ProjectStatusHistory]:
        stmt = (
            select(ProjectStatusHistoryModel)
            .where(ProjectStatusHistoryModel.project_id == project_id)
            .order_by(ProjectStatusHistoryModel.changed_at.asc())
        )
        if limit is not None:
            stmt = stmt.limit(limit).offset(offset or 0)
        result = await self._session.execute(stmt)
        return [to_domain_project_status_history(row) for row in result.scalars().all()]

    async def count_by_project(self, project_id: EntityId) -> int:
        result = await self._session.execute(
            select(func.count(ProjectStatusHistoryModel.id)).where(
                ProjectStatusHistoryModel.project_id == project_id,
            )
        )
        return int(result.scalar_one())
