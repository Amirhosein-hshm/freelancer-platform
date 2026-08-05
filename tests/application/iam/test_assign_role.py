from datetime import UTC, datetime

import pytest

from app.application.iam.dto import AssignRoleCommand
from app.application.iam.use_cases.assign_role import AssignRoleUseCase
from app.application.shared.exceptions import PermissionDeniedError
from app.domain.iam.entities import UserRole
from app.domain.iam.exceptions import RoleAlreadyAssignedError, RoleNotFoundError, UserNotFoundError

NOW = datetime(2026, 8, 2, tzinfo=UTC)


def build_use_case(
    authorization_service, user_repo, role_repo, user_role_repo, id_generator, clock, uow
) -> AssignRoleUseCase:
    return AssignRoleUseCase(
        authorization_service=authorization_service,
        user_repo=user_repo,
        role_repo=role_repo,
        user_role_repo=user_role_repo,
        id_generator=id_generator,
        clock=clock,
        uow=uow,
    )


class TestAssignRoleUseCase:
    async def test_assign_role_success(
        self,
        authorization_service,
        user_repo,
        role_repo,
        user_role_repo,
        id_generator,
        clock,
        uow,
        make_user,
    ):
        authorization_service.grant("admin", "user.assign_role")
        await make_user(user_id="u1")
        use_case = build_use_case(
            authorization_service, user_repo, role_repo, user_role_repo, id_generator, clock, uow
        )

        result = await use_case.execute(
            AssignRoleCommand(actor_id="admin", target_user_id="u1", role_key="admin")
        )

        assert result.role_id == "role-admin"
        assert (await user_role_repo.find_active("u1", "role-admin")) is not None
        assert uow.committed is True

    async def test_assign_role_requires_permission(
        self,
        authorization_service,
        user_repo,
        role_repo,
        user_role_repo,
        id_generator,
        clock,
        uow,
        make_user,
    ):
        await make_user(user_id="u1")
        use_case = build_use_case(
            authorization_service, user_repo, role_repo, user_role_repo, id_generator, clock, uow
        )

        with pytest.raises(PermissionDeniedError):
            await use_case.execute(AssignRoleCommand(actor_id="admin", target_user_id="u1", role_key="admin"))

    async def test_assign_role_duplicate_raises(
        self,
        authorization_service,
        user_repo,
        role_repo,
        user_role_repo,
        id_generator,
        clock,
        uow,
        make_user,
    ):
        authorization_service.grant("admin", "user.assign_role")
        await make_user(user_id="u1")
        await user_role_repo.add(
            UserRole(
                id="ur-1",
                user_id="u1",
                role_id="role-admin",
                assigned_by_user_id="admin",
                assigned_at=NOW,
                created_at=NOW,
            )
        )
        use_case = build_use_case(
            authorization_service, user_repo, role_repo, user_role_repo, id_generator, clock, uow
        )

        with pytest.raises(RoleAlreadyAssignedError):
            await use_case.execute(AssignRoleCommand(actor_id="admin", target_user_id="u1", role_key="admin"))

    async def test_assign_role_unknown_role_raises(
        self,
        authorization_service,
        user_repo,
        role_repo,
        user_role_repo,
        id_generator,
        clock,
        uow,
        make_user,
    ):
        authorization_service.grant("admin", "user.assign_role")
        await make_user(user_id="u1")
        use_case = build_use_case(
            authorization_service, user_repo, role_repo, user_role_repo, id_generator, clock, uow
        )

        with pytest.raises(RoleNotFoundError):
            await use_case.execute(AssignRoleCommand(actor_id="admin", target_user_id="u1", role_key="nope"))

    async def test_assign_role_unknown_user_raises(
        self,
        authorization_service,
        user_repo,
        role_repo,
        user_role_repo,
        id_generator,
        clock,
        uow,
    ):
        authorization_service.grant("admin", "user.assign_role")
        use_case = build_use_case(
            authorization_service, user_repo, role_repo, user_role_repo, id_generator, clock, uow
        )

        with pytest.raises(UserNotFoundError):
            await use_case.execute(AssignRoleCommand(actor_id="admin", target_user_id="ghost", role_key="admin"))
