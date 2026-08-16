from datetime import UTC, datetime

import pytest

from app.application.iam.dto import ListPermissionsQuery
from app.application.iam.use_cases.list_permissions import ListPermissionsUseCase
from app.application.shared.exceptions import PermissionDeniedError
from app.domain.iam.entities import Permission

NOW = datetime(2026, 8, 2, tzinfo=UTC)


class TestListPermissionsUseCase:
    def build(self, authorization_service, permission_repo):
        return ListPermissionsUseCase(
            authorization_service=authorization_service,
            permission_repo=permission_repo,
        )

    async def test_list_permissions_requires_permission(self, authorization_service, permission_repo):
        use_case = self.build(authorization_service, permission_repo)

        with pytest.raises(PermissionDeniedError):
            await use_case.execute(ListPermissionsQuery(actor_id="admin"))

    async def test_list_all_permissions(self, authorization_service, permission_repo):
        authorization_service.grant("admin", "user.read")
        await permission_repo.add(
            Permission(
                id="perm-1",
                permission_key="user.read",
                module="user",
                action="read",
                description="Read users",
                is_system=False,
                created_at=NOW,
            )
        )
        await permission_repo.add(
            Permission(
                id="perm-2",
                permission_key="category.manage",
                module="category",
                action="manage",
                description="Manage categories",
                is_system=False,
                created_at=NOW,
            )
        )
        use_case = self.build(authorization_service, permission_repo)

        result = await use_case.execute(ListPermissionsQuery(actor_id="admin"))

        keys = {p.permission_key for p in result.permissions}
        assert keys == {"user.read", "category.manage"}

    async def test_list_permissions_filtered_by_module(self, authorization_service, permission_repo):
        authorization_service.grant("admin", "user.read")
        await permission_repo.add(
            Permission(
                id="perm-1",
                permission_key="user.read",
                module="user",
                action="read",
                created_at=NOW,
            )
        )
        await permission_repo.add(
            Permission(
                id="perm-2",
                permission_key="category.manage",
                module="category",
                action="manage",
                created_at=NOW,
            )
        )
        use_case = self.build(authorization_service, permission_repo)

        result = await use_case.execute(ListPermissionsQuery(actor_id="admin", module="user"))

        assert [p.permission_key for p in result.permissions] == ["user.read"]
