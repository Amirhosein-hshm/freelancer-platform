from datetime import UTC, datetime

import pytest

from app.application.iam.dto import RevokePermissionCommand
from app.application.iam.use_cases.revoke_permission import RevokePermissionUseCase
from app.application.shared.exceptions import PermissionDeniedError
from app.domain.iam.entities import Permission
from app.domain.iam.exceptions import SystemRoleImmutableError

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


class TestRevokePermissionUseCase:
    async def test_revoke_permission_success(
        self, authorization_service, role_repo, permission_repo, role_permission_repo, uow
    ):
        authorization_service.grant("admin", "user.revoke_permission")
        await permission_repo.add(
            Permission(
                id="perm-1",
                permission_key="project.create_own",
                module="project",
                action="create",
                created_at=NOW,
            )
        )
        use_case = build_use_case(authorization_service, role_repo, permission_repo, role_permission_repo, uow)

        result = await use_case.execute(
            RevokePermissionCommand(actor_id="admin", role_id="role-customer", permission_id="perm-1")
        )

        assert result.role_id == "role-customer"
        assert result.permission_id == "perm-1"
        assert uow.committed is True

    async def test_revoke_permission_requires_permission(
        self, authorization_service, role_repo, permission_repo, role_permission_repo, uow
    ):
        await permission_repo.add(
            Permission(
                id="perm-1",
                permission_key="project.create_own",
                module="project",
                action="create",
                created_at=NOW,
            )
        )
        use_case = build_use_case(authorization_service, role_repo, permission_repo, role_permission_repo, uow)

        with pytest.raises(PermissionDeniedError):
            await use_case.execute(
                RevokePermissionCommand(actor_id="admin", role_id="role-customer", permission_id="perm-1")
            )

    async def test_revoke_permission_system_role_raises(
        self, authorization_service, role_repo, permission_repo, role_permission_repo, uow
    ):
        authorization_service.grant("admin", "user.revoke_permission")
        await permission_repo.add(
            Permission(
                id="perm-1",
                permission_key="project.create_own",
                module="project",
                action="create",
                created_at=NOW,
            )
        )
        use_case = build_use_case(authorization_service, role_repo, permission_repo, role_permission_repo, uow)

        with pytest.raises(SystemRoleImmutableError):
            await use_case.execute(
                RevokePermissionCommand(actor_id="admin", role_id="role-system", permission_id="perm-1")
            )
