from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.iam.entities import Permission, RolePermission
from app.domain.iam.repositories import IRolePermissionRepository
from app.domain.shared.types import EntityId
from app.infrastructure.db.models.iam_models import PermissionModel, RolePermissionModel
from app.infrastructure.repositories.permission_repository import to_domain_permission


class SqlAlchemyRolePermissionRepository(IRolePermissionRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, role_permission: RolePermission) -> None:
        self._session.add(
            RolePermissionModel(
                id=role_permission.id,
                role_id=role_permission.role_id,
                permission_id=role_permission.permission_id,
                granted_by_user_id=role_permission.granted_by_user_id,
                granted_at=role_permission.granted_at,
            )
        )

    async def list_permissions_for_role(self, role_id: EntityId) -> list[Permission]:
        result = await self._session.execute(
            select(PermissionModel)
            .join(RolePermissionModel, RolePermissionModel.permission_id == PermissionModel.id)
            .where(RolePermissionModel.role_id == role_id)
            .order_by(PermissionModel.permission_key)
        )
        return [to_domain_permission(row) for row in result.scalars().all()]

    async def remove(self, role_id: EntityId, permission_id: EntityId) -> None:
        result = await self._session.execute(
            select(RolePermissionModel).where(
                RolePermissionModel.role_id == role_id,
                RolePermissionModel.permission_id == permission_id,
            )
        )
        row = result.scalars().first()
        if row is not None:
            await self._session.delete(row)
