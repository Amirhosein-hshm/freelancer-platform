from datetime import datetime

from app.application.shared.ports import IIdGenerator
from app.domain.project.entities import ProjectStatusHistory
from app.domain.project.enums import ProjectStatus
from app.domain.project.repositories import IProjectStatusHistoryRepository
from app.domain.shared.types import EntityId


async def record_status_history(
    history_repo: IProjectStatusHistoryRepository,
    id_generator: IIdGenerator,
    project_id: EntityId,
    from_status: ProjectStatus | None,
    to_status: ProjectStatus,
    changed_by: EntityId,
    reason: str | None,
    at: datetime,
) -> None:
    await history_repo.add(
        ProjectStatusHistory(
            id=await id_generator.new_id(),
            project_id=project_id,
            from_status=from_status,
            to_status=to_status,
            changed_by_user_id=changed_by,
            reason=reason,
            changed_at=at,
            created_at=at,
        )
    )
