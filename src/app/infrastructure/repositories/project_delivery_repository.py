from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.project.entities import ProjectDelivery
from app.domain.project.exceptions import DeliveryNotFoundError
from app.domain.project.repositories import IProjectDeliveryRepository
from app.domain.shared.types import EntityId
from app.infrastructure.db.models.project_models import ProjectDeliveryModel
from app.infrastructure.repositories.project_mapping import to_domain_project_delivery


class SqlAlchemyProjectDeliveryRepository(IProjectDeliveryRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, delivery: ProjectDelivery) -> None:
        self._session.add(
            ProjectDeliveryModel(
                id=delivery.id,
                project_id=delivery.project_id,
                version_no=delivery.version_no,
                submitted_by_user_id=delivery.submitted_by_user_id,
                status=delivery.status.value,
                delivery_note=delivery.delivery_note,
                submitted_at=delivery.submitted_at,
                reviewed_at=delivery.reviewed_at,
                reviewer_user_id=delivery.reviewer_user_id,
                superseded_by_delivery_id=delivery.superseded_by_delivery_id,
                file_asset_ids=list(delivery.file_asset_ids),
            )
        )

    async def get_by_id(self, delivery_id: EntityId) -> ProjectDelivery:
        row = await self._session.get(ProjectDeliveryModel, delivery_id)
        if row is None:
            raise DeliveryNotFoundError(f"Delivery {delivery_id} not found.")
        return to_domain_project_delivery(row)

    async def get_latest_for_project(self, project_id: EntityId) -> ProjectDelivery | None:
        result = await self._session.execute(
            select(ProjectDeliveryModel)
            .where(ProjectDeliveryModel.project_id == project_id)
            .order_by(ProjectDeliveryModel.version_no.desc())
            .limit(1)
        )
        row = result.scalar_one_or_none()
        return to_domain_project_delivery(row) if row is not None else None

    async def list_by_project(self, project_id: EntityId) -> list[ProjectDelivery]:
        result = await self._session.execute(
            select(ProjectDeliveryModel)
            .where(ProjectDeliveryModel.project_id == project_id)
            .order_by(ProjectDeliveryModel.version_no.desc())
        )
        return [to_domain_project_delivery(row) for row in result.scalars().all()]

    async def list_by_file_asset_id(self, file_asset_id: EntityId) -> list[ProjectDelivery]:
        result = await self._session.execute(
            select(ProjectDeliveryModel).where(
                ProjectDeliveryModel.file_asset_ids.contains([file_asset_id])
            )
        )
        return [to_domain_project_delivery(row) for row in result.scalars().all()]

    async def update(self, delivery: ProjectDelivery) -> None:
        row = await self._session.get(ProjectDeliveryModel, delivery.id)
        if row is None:
            raise DeliveryNotFoundError(f"Delivery {delivery.id} not found.")
        row.project_id = delivery.project_id
        row.version_no = delivery.version_no
        row.submitted_by_user_id = delivery.submitted_by_user_id
        row.status = delivery.status.value
        row.delivery_note = delivery.delivery_note
        row.submitted_at = delivery.submitted_at
        row.reviewed_at = delivery.reviewed_at
        row.reviewer_user_id = delivery.reviewer_user_id
        row.superseded_by_delivery_id = delivery.superseded_by_delivery_id
        row.file_asset_ids = list(delivery.file_asset_ids)
