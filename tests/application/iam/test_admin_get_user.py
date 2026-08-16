from datetime import datetime

import pytest

from app.application.iam.dto import AdminGetUserQuery
from app.application.iam.use_cases.admin_get_user import AdminGetUserUseCase
from app.application.shared.exceptions import PermissionDeniedError
from app.domain.iam.entities import UserRole
from app.domain.iam.exceptions import UserNotFoundError

NOW = datetime(2026, 8, 2)


class TestAdminGetUserUseCase:
    def build(self, authorization_service, user_repo, user_role_repo):
        return AdminGetUserUseCase(
            authorization_service=authorization_service,
            user_repo=user_repo,
            user_role_repo=user_role_repo,
        )

    async def test_get_user_requires_permission(self, authorization_service, user_repo, user_role_repo, make_user):
        await make_user(user_id="u1")
        use_case = self.build(authorization_service, user_repo, user_role_repo)

        with pytest.raises(PermissionDeniedError):
            await use_case.execute(AdminGetUserQuery(actor_id="admin", target_user_id="u1"))

    async def test_returns_user_with_active_roles(self, authorization_service, user_repo, user_role_repo, make_user):
        authorization_service.grant("admin", "user.read")
        await make_user(
            user_id="u1",
            email="jane@example.com",
            email_verified_at=NOW,
        )
        await user_role_repo.add(
            UserRole(
                id="u1-role-customer",
                user_id="u1",
                role_id="role-customer",
                assigned_by_user_id="admin",
                assigned_at=NOW,
                created_at=NOW,
            )
        )
        use_case = self.build(authorization_service, user_repo, user_role_repo)

        result = await use_case.execute(AdminGetUserQuery(actor_id="admin", target_user_id="u1"))

        assert result.user_id == "u1"
        assert result.email == "jane@example.com"
        assert result.first_name == "John"
        assert result.last_name == "Doe"
        assert result.status == "active"
        assert result.email_verified_at == NOW
        assert result.phone is None
        assert result.last_login_at is None
        assert result.roles == ["customer"]

    async def test_returns_user_with_no_roles(self, authorization_service, user_repo, user_role_repo, make_user):
        authorization_service.grant("admin", "user.read")
        await make_user(user_id="u1")
        use_case = self.build(authorization_service, user_repo, user_role_repo)

        result = await use_case.execute(AdminGetUserQuery(actor_id="admin", target_user_id="u1"))

        assert result.roles == []

    async def test_unknown_user_raises(self, authorization_service, user_repo, user_role_repo):
        authorization_service.grant("admin", "user.read")
        use_case = self.build(authorization_service, user_repo, user_role_repo)

        with pytest.raises(UserNotFoundError):
            await use_case.execute(AdminGetUserQuery(actor_id="admin", target_user_id="ghost"))
