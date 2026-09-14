from datetime import UTC, datetime

import pytest

from app.application.iam.dto import RevokePermissionCommand
from app.application.iam.use_cases.revoke_permission import RevokePermissionUseCase
from app.application.shared.exceptions import PermissionDeniedError
from app.domain.iam.entities import Permission, RolePermission
from app.domain.iam.exceptions import PermissionNotFoundError, RoleNotFoundError

NOW = datetime(2026, 8, 2, tzinfo=UTC)


def build_use_case(
    authorization_service, role_repo, permission_repo, role_permission_repo, uow
) -> RevokePermissionUseCase:
    return RevokePermissionUseCase(
        authorization_service=authorization_service,
        role_repo=role_repo,
        permission_repo=permission_repo,
        role_permission_repo=role_permission_repo,
        uow=uow,
    )


async def seed_permission(permission_repo, permission_id: str = "perm-1") -> None:
    await permission_repo.add(
        Permission(
            id=permission_id,
            permission_key="project.create_own",
            module="project",
            action="create",
            created_at=NOW,
        )
    )


async def seed_grant(role_permission_repo, role_id: str, permission_id: str = "perm-1") -> None:
    await role_permission_repo.add(
        RolePermission(
            id=f"{role_id}-{permission_id}",
            role_id=role_id,
            permission_id=permission_id,
            granted_by_user_id="admin",
            granted_at=NOW,
            created_at=NOW,
        )
    )


class TestRevokePermissionUseCase:
    async def test_revoke_permission_success(
        self, authorization_service, role_repo, permission_repo, role_permission_repo, uow
    ):
        authorization_service.grant("admin", "user.revoke_permission")
        await seed_permission(permission_repo)
        await seed_grant(role_permission_repo, "role-customer")
        use_case = build_use_case(authorization_service, role_repo, permission_repo, role_permission_repo, uow)

        result = await use_case.execute(
            RevokePermissionCommand(actor_id="admin", role_id="role-customer", permission_id="perm-1")
        )

        assert result.role_id == "role-customer"
        assert result.permission_id == "perm-1"
        assert uow.committed is True
        assert await role_permission_repo.list_permissions_for_role("role-customer") == []

    async def test_revoke_permission_requires_permission(
        self, authorization_service, role_repo, permission_repo, role_permission_repo, uow
    ):
        await seed_permission(permission_repo)
        use_case = build_use_case(authorization_service, role_repo, permission_repo, role_permission_repo, uow)

        with pytest.raises(PermissionDeniedError):
            await use_case.execute(
                RevokePermissionCommand(actor_id="admin", role_id="role-customer", permission_id="perm-1")
            )

    async def test_revoke_permission_from_admin_role_succeeds(
        self, authorization_service, role_repo, permission_repo, role_permission_repo, uow
    ):
        """Revoking a permission from `admin` is legitimate RBAC configuration, not catalog mutation."""
        authorization_service.grant("admin", "user.revoke_permission")
        await seed_permission(permission_repo)
        await seed_grant(role_permission_repo, "role-admin")
        use_case = build_use_case(authorization_service, role_repo, permission_repo, role_permission_repo, uow)

        result = await use_case.execute(
            RevokePermissionCommand(actor_id="admin", role_id="role-admin", permission_id="perm-1")
        )

        assert result.role_id == "role-admin"
        assert await role_permission_repo.list_permissions_for_role("role-admin") == []

    async def test_revoke_permission_from_is_system_role_succeeds(
        self, authorization_service, role_repo, permission_repo, role_permission_repo, uow
    ):
        """`is_system` protects the Role catalog entity, never the RolePermission link."""
        authorization_service.grant("admin", "user.revoke_permission")
        await seed_permission(permission_repo)
        await seed_grant(role_permission_repo, "role-system")
        use_case = build_use_case(authorization_service, role_repo, permission_repo, role_permission_repo, uow)

        result = await use_case.execute(
            RevokePermissionCommand(actor_id="admin", role_id="role-system", permission_id="perm-1")
        )

        assert result.role_id == "role-system"
        assert await role_permission_repo.list_permissions_for_role("role-system") == []

    async def test_revoke_permission_unknown_role_raises(
        self, authorization_service, role_repo, permission_repo, role_permission_repo, uow
    ):
        authorization_service.grant("admin", "user.revoke_permission")
        await seed_permission(permission_repo)
        use_case = build_use_case(authorization_service, role_repo, permission_repo, role_permission_repo, uow)

        with pytest.raises(RoleNotFoundError):
            await use_case.execute(
                RevokePermissionCommand(actor_id="admin", role_id="role-ghost", permission_id="perm-1")
            )

    async def test_revoke_permission_unknown_permission_raises(
        self, authorization_service, role_repo, permission_repo, role_permission_repo, uow
    ):
        authorization_service.grant("admin", "user.revoke_permission")
        use_case = build_use_case(authorization_service, role_repo, permission_repo, role_permission_repo, uow)

        with pytest.raises(PermissionNotFoundError):
            await use_case.execute(
                RevokePermissionCommand(actor_id="admin", role_id="role-customer", permission_id="perm-ghost")
            )
