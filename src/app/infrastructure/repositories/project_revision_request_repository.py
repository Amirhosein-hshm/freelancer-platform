from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.project.entities import ProjectRevisionRequest
from app.domain.project.repositories import IProjectRevisionRequestRepository
from app.domain.shared.exceptions import EntityNotFoundError
from app.domain.shared.types import EntityId
from app.infrastructure.db.models.project_models import ProjectRevisionRequestModel
from app.infrastructure.repositories.project_mapping import (
    to_domain_project_revision_request,
)


class SqlAlchemyProjectRevisionRequestRepository(IProjectRevisionRequestRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, revision: ProjectRevisionRequest) -> None:
        self._session.add(
            ProjectRevisionRequestModel(
                id=revision.id,
                project_id=revision.project_id,
                project_delivery_id=revision.project_delivery_id,
                requested_by_user_id=revision.requested_by_user_id,
                requested_to_user_id=revision.requested_to_user_id,
                round_no=revision.round_no,
                status=revision.status.value,
                reason=revision.reason,
                resolved_by_user_id=revision.resolved_by_user_id,
                requested_at=revision.requested_at,
                resolved_at=revision.resolved_at,
            )
        )

    async def list_by_project(
        self,
        project_id: EntityId,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[ProjectRevisionRequest]:
        stmt = (
            select(ProjectRevisionRequestModel)
            .where(ProjectRevisionRequestModel.project_id == project_id)
            .order_by(ProjectRevisionRequestModel.requested_at.asc())
        )
        if limit is not None:
            stmt = stmt.limit(limit).offset(offset or 0)
        result = await self._session.execute(stmt)
        return [to_domain_project_revision_request(row) for row in result.scalars().all()]

    async def count_by_project(self, project_id: EntityId) -> int:
        result = await self._session.execute(
            select(func.count(ProjectRevisionRequestModel.id)).where(
                ProjectRevisionRequestModel.project_id == project_id
            )
        )
        return int(result.scalar_one())

    async def update(self, revision: ProjectRevisionRequest) -> None:
        row = await self._session.get(ProjectRevisionRequestModel, revision.id)
        if row is None:
            raise EntityNotFoundError(f"Revision request {revision.id} not found.")
        row.project_delivery_id = revision.project_delivery_id
        row.requested_by_user_id = revision.requested_by_user_id
        row.requested_to_user_id = revision.requested_to_user_id
        row.round_no = revision.round_no
        row.status = revision.status.value
        row.reason = revision.reason
        row.resolved_by_user_id = revision.resolved_by_user_id
        row.requested_at = revision.requested_at
        row.resolved_at = revision.resolved_at
