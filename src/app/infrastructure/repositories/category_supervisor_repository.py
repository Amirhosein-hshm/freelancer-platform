from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.category.entities import CategorySupervisor
from app.domain.category.exceptions import SupervisorAssignmentNotFoundError
from app.domain.category.repositories import ICategorySupervisorRepository
from app.domain.shared.types import EntityId
from app.infrastructure.db.models.category_models import CategorySupervisorModel
from app.infrastructure.repositories.category_mapping import to_domain_category_supervisor


class SqlAlchemyCategorySupervisorRepository(ICategorySupervisorRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, link: CategorySupervisor) -> None:
        self._session.add(
            CategorySupervisorModel(
                id=link.id,
                category_id=link.category_id,
                supervisor_user_id=link.supervisor_user_id,
                assigned_by_user_id=link.assigned_by_user_id,
                is_primary=link.is_primary,
                is_active=link.is_active,
                assigned_at=link.assigned_at,
                revoked_at=link.revoked_at,
            )
        )

    async def list_active_supervisors(
        self, category_id: EntityId
    ) -> list[CategorySupervisor]:
        result = await self._session.execute(
            select(CategorySupervisorModel)
            .where(
                CategorySupervisorModel.category_id == category_id,
                CategorySupervisorModel.is_active.is_(True),
            )
            .order_by(CategorySupervisorModel.is_primary.desc(), CategorySupervisorModel.assigned_at.asc())
        )
        return [to_domain_category_supervisor(row) for row in result.scalars().all()]

    async def list_categories_for_supervisor(
        self, supervisor_user_id: EntityId
    ) -> list[EntityId]:
        result = await self._session.execute(
            select(CategorySupervisorModel.category_id)
            .where(
                CategorySupervisorModel.supervisor_user_id == supervisor_user_id,
                CategorySupervisorModel.is_active.is_(True),
            )
        )
        return list(result.scalars().all())

    async def is_supervisor_of(
        self, supervisor_user_id: EntityId, category_id: EntityId
    ) -> bool:
        result = await self._session.execute(
            select(CategorySupervisorModel.id)
            .where(
                CategorySupervisorModel.supervisor_user_id == supervisor_user_id,
                CategorySupervisorModel.category_id == category_id,
                CategorySupervisorModel.is_active.is_(True),
            )
            .limit(1)
        )
        return result.scalar_one_or_none() is not None

    async def update(self, link: CategorySupervisor) -> None:
        row = await self._session.get(CategorySupervisorModel, link.id)
        if row is None:
            raise SupervisorAssignmentNotFoundError(
                f"Category supervisor link {link.id} not found."
            )
        row.category_id = link.category_id
        row.supervisor_user_id = link.supervisor_user_id
        row.assigned_by_user_id = link.assigned_by_user_id
        row.is_primary = link.is_primary
        row.is_active = link.is_active
        row.assigned_at = link.assigned_at
        row.revoked_at = link.revoked_at