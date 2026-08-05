from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.shared.authorization import IAuthorizationService
from app.application.shared.exceptions import PermissionDeniedError
from app.domain.shared.types import EntityId
from app.infrastructure.db.models.iam_models import (
    PermissionModel,
    RoleModel,
    RolePermissionModel,
    UserRoleModel,
)


class SqlAlchemyAuthorizationService(IAuthorizationService):
    """Resolves permission checks through a real ``user_roles → role_permissions →
    permissions`` join — never a hardcoded ``if role == "admin"`` shortcut.

    See AUTHORIZATION.md §6 for the binding data-source contract.
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def _permission_keys_for_user(self, user_id: EntityId) -> set[str]:
        result = await self._session.execute(
            select(PermissionModel.permission_key)
            .join(RolePermissionModel, RolePermissionModel.permission_id == PermissionModel.id)
            .join(UserRoleModel, UserRoleModel.role_id == RolePermissionModel.role_id)
            .where(
                UserRoleModel.user_id == user_id,
                UserRoleModel.is_active.is_(True),
            )
        )
        return set(result.scalars().all())

    async def has_permission(self, user_id: EntityId, permission_key: str) -> bool:
        keys = await self._permission_keys_for_user(user_id)
        return permission_key in keys

    async def require_permission(self, user_id: EntityId, permission_key: str) -> None:
        if not await self.has_permission(user_id, permission_key):
            raise PermissionDeniedError(
                f"User {user_id} does not have permission '{permission_key}'."
            )

    async def has_role(self, user_id: EntityId, role_key: str) -> bool:
        result = await self._session.execute(
            select(UserRoleModel.id)
            .join(RoleModel, RoleModel.id == UserRoleModel.role_id)
            .where(
                UserRoleModel.user_id == user_id,
                RoleModel.role_key == role_key,
                UserRoleModel.is_active.is_(True),
            )
            .limit(1)
        )
        return result.scalar_one_or_none() is not None

    async def list_permissions_for_user(self, user_id: EntityId) -> list[str]:
        return sorted(await self._permission_keys_for_user(user_id))