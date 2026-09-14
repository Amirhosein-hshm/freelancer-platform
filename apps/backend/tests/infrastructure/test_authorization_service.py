"""SqlAlchemyAuthorizationService integration tests.

Proves AUTHORIZATION.md §6's data-source contract: permission checks resolve
through the real ``user_roles -> role_permissions -> permissions`` DB join, and
revoking a permission in the DB changes the authorization outcome (no hardcoded
shortcut).
"""

from datetime import UTC, datetime

import pytest

from app.infrastructure.db.models.iam_models import (
    PermissionModel,
    RoleModel,
    RolePermissionModel,
    UserModel,
    UserRoleModel,
)
from app.infrastructure.security.authorization_service import (
    SqlAlchemyAuthorizationService,
)

pytestmark = pytest.mark.integration


def _now() -> datetime:
    return datetime(2026, 8, 2, tzinfo=UTC)


async def _seed_graph(db_session) -> tuple[str, str]:
    """Persist user, role, permission, user_role, role_permission rows.

    Returns ``(user_id, permission_key)``.
    """
    user_id = "user-1"
    role_id = "role-1"
    permission_id = "perm-1"
    permission_key = "project.create_own"
    now = _now()

    db_session.add(
        UserModel(
            id=user_id,
            email="test@example.com",
            phone=None,
            password_hash="hash",
            first_name="Jane",
            last_name="Doe",
            status="active",
            created_at=now,
        )
    )
    db_session.add(RoleModel(id=role_id, role_key="customer", name="Customer", is_system=True, created_at=now))
    db_session.add(
        PermissionModel(
            id=permission_id,
            permission_key=permission_key,
            module="project",
            action="create_own",
            is_system=True,
            created_at=now,
        )
    )
    db_session.add(
        UserRoleModel(
            id="ur-1",
            user_id=user_id,
            role_id=role_id,
            assigned_by_user_id="system",
            assigned_at=now,
            revoked_at=None,
            is_active=True,
            created_at=now,
        )
    )
    db_session.add(
        RolePermissionModel(
            id="rp-1",
            role_id=role_id,
            permission_id=permission_id,
            granted_by_user_id="system",
            granted_at=now,
        )
    )
    await db_session.commit()
    return user_id, permission_key


async def test_has_permission_true_for_seeded_pair(db_session) -> None:
    user_id, key = await _seed_graph(db_session)
    service = SqlAlchemyAuthorizationService(db_session)
    assert await service.has_permission(user_id, key) is True
    assert await service.has_permission(user_id, "reporting.read") is False
    assert (await service.list_permissions_for_user(user_id)) == [key]
    assert await service.has_role(user_id, "customer") is True
    assert await service.has_role(user_id, "admin") is False


async def test_revoking_permission_changes_authz_outcome(db_session) -> None:
    user_id, key = await _seed_graph(db_session)
    service = SqlAlchemyAuthorizationService(db_session)
    assert await service.has_permission(user_id, key) is True

    row = await db_session.get(RolePermissionModel, "rp-1")
    await db_session.delete(row)
    await db_session.commit()

    assert await service.has_permission(user_id, key) is False
    assert "project.create_own" not in await service.list_permissions_for_user(user_id)


async def test_require_permission_raises_permission_denied(db_session) -> None:
    from app.application.shared.exceptions import PermissionDeniedError

    user_id, _ = await _seed_graph(db_session)
    service = SqlAlchemyAuthorizationService(db_session)
    await service.require_permission(user_id, "project.create_own")
    with pytest.raises(PermissionDeniedError):
        await service.require_permission(user_id, "user.delete")
