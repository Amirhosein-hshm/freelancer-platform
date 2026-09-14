from datetime import UTC, datetime

import pytest

from app.application.iam.dto import RemoveRoleCommand
from app.application.iam.use_cases.remove_role import RemoveRoleUseCase
from app.application.shared.exceptions import PermissionDeniedError
from app.domain.iam.entities import UserRole
from app.domain.iam.exceptions import (
    LastAdminRoleRemovalError,
    RoleNotFoundError,
    UserNotFoundError,
    UserRoleNotFoundError,
)

NOW = datetime(2026, 8, 2, tzinfo=UTC)


def build_use_case(authorization_service, user_repo, role_repo, user_role_repo, clock, uow) -> RemoveRoleUseCase:
    return RemoveRoleUseCase(
        authorization_service=authorization_service,
        user_repo=user_repo,
        role_repo=role_repo,
        user_role_repo=user_role_repo,
        clock=clock,
        uow=uow,
    )


async def seed_link(user_role_repo, user_id: str, role_id: str) -> None:
    await user_role_repo.add(
        UserRole(
            id=f"{user_id}-{role_id}",
            user_id=user_id,
            role_id=role_id,
            assigned_by_user_id="admin",
            assigned_at=NOW,
            created_at=NOW,
        )
    )


class TestRemoveRoleUseCase:
    async def test_remove_role_success(
        self, authorization_service, user_repo, role_repo, user_role_repo, clock, uow, make_user
    ):
        authorization_service.grant("admin", "user.remove_role")
        await make_user(user_id="u1")
        await seed_link(user_role_repo, "u1", "role-customer")
        use_case = build_use_case(authorization_service, user_repo, role_repo, user_role_repo, clock, uow)

        result = await use_case.execute(RemoveRoleCommand(actor_id="admin", target_user_id="u1", role_key="customer"))

        assert result.revoked_at == NOW
        assert (await user_role_repo.find_active("u1", "role-customer")) is None

    async def test_remove_freelancer_role_success(
        self, authorization_service, user_repo, role_repo, user_role_repo, clock, uow, make_user
    ):
        authorization_service.grant("admin", "user.remove_role")
        await make_user(user_id="u1")
        await seed_link(user_role_repo, "u1", "role-freelancer")
        use_case = build_use_case(authorization_service, user_repo, role_repo, user_role_repo, clock, uow)

        result = await use_case.execute(RemoveRoleCommand(actor_id="admin", target_user_id="u1", role_key="freelancer"))

        assert result.role_id == "role-freelancer"
        assert (await user_role_repo.find_active("u1", "role-freelancer")) is None

    async def test_remove_role_requires_permission(
        self, authorization_service, user_repo, role_repo, user_role_repo, clock, uow, make_user
    ):
        await make_user(user_id="u1")
        use_case = build_use_case(authorization_service, user_repo, role_repo, user_role_repo, clock, uow)

        with pytest.raises(PermissionDeniedError):
            await use_case.execute(RemoveRoleCommand(actor_id="admin", target_user_id="u1", role_key="admin"))

    async def test_remove_link_of_is_system_role_succeeds(
        self, authorization_service, user_repo, role_repo, user_role_repo, clock, uow, make_user
    ):
        """`is_system` protects the Role catalog entity, never the UserRole link."""
        authorization_service.grant("admin", "user.remove_role")
        await make_user(user_id="u1")
        await seed_link(user_role_repo, "u1", "role-system")
        use_case = build_use_case(authorization_service, user_repo, role_repo, user_role_repo, clock, uow)

        result = await use_case.execute(RemoveRoleCommand(actor_id="admin", target_user_id="u1", role_key="system"))

        assert result.role_id == "role-system"
        assert (await user_role_repo.find_active("u1", "role-system")) is None

    async def test_remove_admin_role_allowed_when_another_admin_remains(
        self, authorization_service, user_repo, role_repo, user_role_repo, clock, uow, make_user
    ):
        authorization_service.grant("admin", "user.remove_role")
        await make_user(user_id="admin-1")
        await make_user(user_id="admin-2", email="admin2@example.com")
        await seed_link(user_role_repo, "admin-1", "role-admin")
        await seed_link(user_role_repo, "admin-2", "role-admin")
        use_case = build_use_case(authorization_service, user_repo, role_repo, user_role_repo, clock, uow)

        result = await use_case.execute(
            RemoveRoleCommand(actor_id="admin", target_user_id="admin-1", role_key="admin")
        )

        assert result.user_id == "admin-1"
        assert (await user_role_repo.find_active("admin-1", "role-admin")) is None
        assert (await user_role_repo.find_active("admin-2", "role-admin")) is not None

    async def test_remove_last_admin_role_raises(
        self, authorization_service, user_repo, role_repo, user_role_repo, clock, uow, make_user
    ):
        authorization_service.grant("admin", "user.remove_role")
        await make_user(user_id="admin-1")
        await seed_link(user_role_repo, "admin-1", "role-admin")
        use_case = build_use_case(authorization_service, user_repo, role_repo, user_role_repo, clock, uow)

        with pytest.raises(LastAdminRoleRemovalError):
            await use_case.execute(RemoveRoleCommand(actor_id="admin", target_user_id="admin-1", role_key="admin"))

        assert (await user_role_repo.find_active("admin-1", "role-admin")) is not None
        assert uow.committed is False

    async def test_remove_own_admin_role_as_last_admin_raises(
        self, authorization_service, user_repo, role_repo, user_role_repo, clock, uow, make_user
    ):
        authorization_service.grant("admin-1", "user.remove_role")
        await make_user(user_id="admin-1")
        await seed_link(user_role_repo, "admin-1", "role-admin")
        use_case = build_use_case(authorization_service, user_repo, role_repo, user_role_repo, clock, uow)

        with pytest.raises(LastAdminRoleRemovalError):
            await use_case.execute(RemoveRoleCommand(actor_id="admin-1", target_user_id="admin-1", role_key="admin"))

    async def test_remove_role_without_active_assignment_raises(
        self, authorization_service, user_repo, role_repo, user_role_repo, clock, uow, make_user
    ):
        authorization_service.grant("admin", "user.remove_role")
        await make_user(user_id="u1")
        use_case = build_use_case(authorization_service, user_repo, role_repo, user_role_repo, clock, uow)

        with pytest.raises(UserRoleNotFoundError):
            await use_case.execute(RemoveRoleCommand(actor_id="admin", target_user_id="u1", role_key="admin"))

    async def test_remove_role_unknown_role_raises(
        self, authorization_service, user_repo, role_repo, user_role_repo, clock, uow, make_user
    ):
        authorization_service.grant("admin", "user.remove_role")
        await make_user(user_id="u1")
        use_case = build_use_case(authorization_service, user_repo, role_repo, user_role_repo, clock, uow)

        with pytest.raises(RoleNotFoundError):
            await use_case.execute(RemoveRoleCommand(actor_id="admin", target_user_id="u1", role_key="nope"))

    async def test_remove_role_unknown_user_raises(
        self, authorization_service, user_repo, role_repo, user_role_repo, clock, uow
    ):
        authorization_service.grant("admin", "user.remove_role")
        use_case = build_use_case(authorization_service, user_repo, role_repo, user_role_repo, clock, uow)

        with pytest.raises(UserNotFoundError):
            await use_case.execute(RemoveRoleCommand(actor_id="admin", target_user_id="ghost", role_key="admin"))
