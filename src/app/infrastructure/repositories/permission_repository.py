from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.iam.entities import Permission
from app.domain.iam.exceptions import PermissionNotFoundError
from app.domain.iam.repositories import IPermissionRepository
from app.domain.shared.types import EntityId
from app.infrastructure.db.models.iam_models import PermissionModel


def to_domain_permission(row: object) -> Permission:
    return Permission(
        id=row.id,
        permission_key=row.permission_key,
        module=row.module,
        action=row.action,
        description=row.description,
        is_system=row.is_system,
        created_at=row.created_at,
    )


class SqlAlchemyPermissionRepository(IPermissionRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, permission_id: EntityId) -> Permission:
        row = await self._session.get(PermissionModel, permission_id)
        if row is None:
            raise PermissionNotFoundError(f"Permission {permission_id} not found.")
        return to_domain_permission(row)

    async def list_all(self) -> list[Permission]:
        result = await self._session.execute(
            select(PermissionModel).order_by(PermissionModel.module, PermissionModel.permission_key)
        )
        return [to_domain_permission(row) for row in result.scalars().all()]

    async def list_by_module(self, module: str) -> list[Permission]:
        result = await self._session.execute(
            select(PermissionModel).where(PermissionModel.module == module).order_by(PermissionModel.permission_key)
        )
        return [to_domain_permission(row) for row in result.scalars().all()]
