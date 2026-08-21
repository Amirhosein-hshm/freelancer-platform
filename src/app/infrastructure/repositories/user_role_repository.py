from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.iam.entities import Role, UserRole
from app.domain.iam.exceptions import UserRoleNotFoundError
from app.domain.iam.repositories import IUserRoleRepository
from app.domain.shared.types import EntityId
from app.infrastructure.db.models.iam_models import RoleModel, UserModel, UserRoleModel
from app.infrastructure.repositories.role_repository import to_domain_role


def to_domain_user_role(row: object) -> UserRole:
    return UserRole(
        id=row.id,
        user_id=row.user_id,
        role_id=row.role_id,
        assigned_by_user_id=row.assigned_by_user_id,
        assigned_at=row.assigned_at,
        revoked_at=row.revoked_at,
        is_active=row.is_active,
        created_at=row.created_at,
    )


class SqlAlchemyUserRoleRepository(IUserRoleRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, user_role: UserRole) -> None:
        self._session.add(
            UserRoleModel(
                id=user_role.id,
                user_id=user_role.user_id,
                role_id=user_role.role_id,
                assigned_by_user_id=user_role.assigned_by_user_id,
                assigned_at=user_role.assigned_at,
                revoked_at=user_role.revoked_at,
                is_active=user_role.is_active,
                created_at=user_role.created_at,
            )
        )

    async def find_active(self, user_id: EntityId, role_id: EntityId) -> UserRole | None:
        result = await self._session.execute(
            select(UserRoleModel).where(
                UserRoleModel.user_id == user_id,
                UserRoleModel.role_id == role_id,
                UserRoleModel.is_active.is_(True),
            )
        )
        row = result.scalars().first()
        return to_domain_user_role(row) if row is not None else None

    async def list_active_roles_for_user(self, user_id: EntityId) -> list[Role]:
        result = await self._session.execute(
            select(RoleModel)
            .join(UserRoleModel, UserRoleModel.role_id == RoleModel.id)
            .where(UserRoleModel.user_id == user_id, UserRoleModel.is_active.is_(True))
        )
        return [to_domain_role(row) for row in result.scalars().all()]

    async def list_active_user_ids_for_role(self, role_id: EntityId) -> list[EntityId]:
        """Soft-deleted users are excluded: a deleted admin must not satisfy the
        last-admin guards in ``RemoveRoleUseCase``/``AdminDeleteUserUseCase``."""
        result = await self._session.execute(
            select(UserRoleModel.user_id)
            .join(UserModel, UserModel.id == UserRoleModel.user_id)
            .where(
                UserRoleModel.role_id == role_id,
                UserRoleModel.is_active.is_(True),
                UserModel.deleted_at.is_(None),
            )
        )
        return list(result.scalars().all())

    async def update(self, user_role: UserRole) -> None:
        row = await self._session.get(UserRoleModel, user_role.id)
        if row is None:
            raise UserRoleNotFoundError(f"UserRole {user_role.id} not found.")
        row.revoked_at = user_role.revoked_at
        row.is_active = user_role.is_active
