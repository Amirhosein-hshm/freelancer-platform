import pytest

from app.application.iam.dto import ListRolesQuery
from app.application.iam.use_cases.list_roles import ListRolesUseCase
from app.application.shared.exceptions import PermissionDeniedError


class TestListRolesUseCase:
    def build(self, authorization_service, role_repo):
        return ListRolesUseCase(
            authorization_service=authorization_service,
            role_repo=role_repo,
        )

    async def test_list_roles_requires_permission(self, authorization_service, role_repo):
        use_case = self.build(authorization_service, role_repo)

        with pytest.raises(PermissionDeniedError):
            await use_case.execute(ListRolesQuery(actor_id="admin"))

    async def test_list_roles_returns_all_roles(self, authorization_service, role_repo):
        authorization_service.grant("admin", "user.read")
        use_case = self.build(authorization_service, role_repo)

        result = await use_case.execute(ListRolesQuery(actor_id="admin"))

        keys = {r.role_key for r in result.roles}
        assert keys == {"customer", "freelancer", "admin", "system"}
        system_role = next(r for r in result.roles if r.role_key == "system")
        assert system_role.is_system is True
