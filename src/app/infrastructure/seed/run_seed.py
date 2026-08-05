"""Idempotent seeding of RBAC roles/permissions and the primary admin user.

Safe to run many times: every role/permission insert uses ``ON CONFLICT DO
NOTHING`` and the admin user is only created when ``admin_email`` is not yet
present. Credentials come from ``infrastructure/config.Settings`` (env vars),
never from code.
"""

import asyncio
from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert

from app.infrastructure.config import get_settings
from app.infrastructure.db.models.iam_models import (
    PermissionModel,
    RoleModel,
    RolePermissionModel,
    UserModel,
    UserRoleModel,
)
from app.infrastructure.db.session import get_session_factory
from app.infrastructure.security.password_hasher import Argon2PasswordHasher
from app.infrastructure.seed.seed_data import ADMIN_PERMISSION_KEYS, PERMISSIONS, ROLE_PERMISSIONS, ROLES

ADMIN_ROLE_KEY = "admin"


async def _seed_roles(session, now: datetime) -> None:
    for role in ROLES:
        await session.execute(
            pg_insert(RoleModel)
            .values(id=str(uuid4()), created_at=now, **role)
            .on_conflict_do_nothing(index_elements=["role_key"])
        )


async def _seed_permissions(session, now: datetime) -> None:
    for permission in PERMISSIONS:
        await session.execute(
            pg_insert(PermissionModel)
            .values(id=str(uuid4()), created_at=now, **permission)
            .on_conflict_do_nothing(index_elements=["permission_key"])
        )


async def _seed_role_permissions(session, now: datetime) -> None:
    roles = {
        role.role_key: role.id
        for role in (await session.execute(select(RoleModel))).scalars().all()
    }
    permissions = {
        permission.permission_key: permission.id
        for permission in (await session.execute(select(PermissionModel))).scalars().all()
    }
    for role_key, permission_keys in ROLE_PERMISSIONS.items():
        role_id = roles.get(role_key)
        if role_id is None:
            continue
        resolved = (
            list(ADMIN_PERMISSION_KEYS)
            if role_key == ADMIN_ROLE_KEY and permission_keys == ["*"]
            else permission_keys
        )
        for permission_key in resolved:
            permission_id = permissions.get(permission_key)
            if permission_id is None:
                continue
            await session.execute(
                pg_insert(RolePermissionModel)
                .values(
                    id=str(uuid4()),
                    role_id=role_id,
                    permission_id=permission_id,
                    granted_by_user_id="system-seed",
                    granted_at=now,
                )
                .on_conflict_do_nothing(index_elements=["role_id", "permission_id"])
            )


async def _seed_admin_user(session, now: datetime) -> None:
    settings = get_settings()
    existing = await session.execute(
        select(UserModel).where(UserModel.email == settings.admin_email)
    )
    if existing.scalar_one_or_none() is not None:
        return
    admin_role_id = (
        await session.execute(
            select(RoleModel).where(RoleModel.role_key == ADMIN_ROLE_KEY)
        )
    ).scalar_one().id
    hasher = Argon2PasswordHasher()
    admin_user = UserModel(
        id=str(uuid4()),
        email=settings.admin_email,
        phone=None,
        password_hash=await hasher.hash(settings.admin_password),
        first_name="System",
        last_name="Admin",
        status="active",
        created_at=now,
        email_verified_at=now,
        phone_verified_at=None,
        last_login_at=None,
        password_changed_at=None,
        deleted_at=None,
    )
    session.add(admin_user)
    await session.flush()
    session.add(
        UserRoleModel(
            id=str(uuid4()),
            user_id=admin_user.id,
            role_id=admin_role_id,
            assigned_by_user_id="system-seed",
            assigned_at=now,
            created_at=now,
            revoked_at=None,
            is_active=True,
        )
    )


async def run_seed() -> None:
    session_factory = get_session_factory()
    async with session_factory() as session:
        now = datetime.now(UTC)
        await _seed_roles(session, now)
        await _seed_permissions(session, now)
        await session.flush()
        await _seed_role_permissions(session, now)
        await _seed_admin_user(session, now)
        await session.commit()


if __name__ == "__main__":
    asyncio.run(run_seed())