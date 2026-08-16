from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.iam.entities import Role
from app.domain.iam.exceptions import RoleNotFoundError
from app.domain.iam.repositories import IRoleRepository
from app.domain.shared.types import EntityId
from app.infrastructure.db.models.iam_models import RoleModel


def to_domain_role(row: object) -> Role:
    return Role(
        id=row.id,
        role_key=row.role_key,
        name=row.name,
        description=row.description,
        is_system=row.is_system,
        created_at=row.created_at,
    )


class SqlAlchemyRoleRepository(IRoleRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, role_id: EntityId) -> Role:
        row = await self._session.get(RoleModel, role_id)
        if row is None:
            raise RoleNotFoundError(f"Role {role_id} not found.")
        return to_domain_role(row)

    async def get_by_key(self, role_key: str) -> Role:
        result = await self._session.execute(select(RoleModel).where(RoleModel.role_key == role_key))
        row = result.scalar_one_or_none()
        if row is None:
            raise RoleNotFoundError(f"Role '{role_key}' not found.")
        return to_domain_role(row)

    async def list_all(self) -> list[Role]:
        result = await self._session.execute(select(RoleModel).order_by(RoleModel.role_key))
        return [to_domain_role(row) for row in result.scalars().all()]

    async def add(self, role: Role) -> None:
        self._session.add(
            RoleModel(
                id=role.id,
                role_key=role.role_key,
                name=role.name,
                description=role.description,
                is_system=role.is_system,
                created_at=role.created_at,
            )
        )
