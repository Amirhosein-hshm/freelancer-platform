from datetime import UTC, datetime

import pytest

from app.application.iam.dto import RemoveRoleCommand
from app.application.iam.use_cases.remove_role import RemoveRoleUseCase
from app.application.shared.exceptions import PermissionDeniedError
from app.domain.iam.entities import UserRole
from app.domain.iam.exceptions import RoleNotFoundError, UserNotFoundError, UserRoleNotFoundError

NOW = datetime(2026, 8, 2, tzinfo=UTC)


def build_use_case(
    authorization_service, user_repo, role_repo, user_role_repo, clock, uow
) -> RemoveRoleUseCase:
    return RemoveRoleUseCase(
        authorization_service=authorization_service,
        user_repo=user_repo,
        role_repo=role_repo,
        user_role_repo=user_role_repo,
        clock=clock,
        uow=uow,
    )


class TestRemoveRoleUseCase:
    def test_remove_role_success(
        self, authorization_service, user_repo, role_repo, user_role_repo, clock, uow, make_user
    ):
        authorization_service.grant("admin", "user.remove_role")
        make_user(user_id="u1")
        user_role_repo.add(
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
            authorization_service, user_repo, role_repo, user_role_repo, clock, uow
        )

        result = use_case.execute(
            RemoveRoleCommand(actor_id="admin", target_user_id="u1", role_key="admin")
        )

        assert result.revoked_at == NOW
        assert user_role_repo.find_active("u1", "role-admin") is None

    def test_remove_role_requires_permission(
        self, authorization_service, user_repo, role_repo, user_role_repo, clock, uow, make_user
    ):
        make_user(user_id="u1")
        use_case = build_use_case(
            authorization_service, user_repo, role_repo, user_role_repo, clock, uow
        )

        with pytest.raises(PermissionDeniedError):
            use_case.execute(
                RemoveRoleCommand(actor_id="admin", target_user_id="u1", role_key="admin")
            )

    def test_remove_role_without_active_assignment_raises(
        self, authorization_service, user_repo, role_repo, user_role_repo, clock, uow, make_user
    ):
        authorization_service.grant("admin", "user.remove_role")
        make_user(user_id="u1")
        use_case = build_use_case(
            authorization_service, user_repo, role_repo, user_role_repo, clock, uow
        )

        with pytest.raises(UserRoleNotFoundError):
            use_case.execute(
                RemoveRoleCommand(actor_id="admin", target_user_id="u1", role_key="admin")
            )

    def test_remove_role_unknown_role_raises(
        self, authorization_service, user_repo, role_repo, user_role_repo, clock, uow, make_user
    ):
        authorization_service.grant("admin", "user.remove_role")
        make_user(user_id="u1")
        use_case = build_use_case(
            authorization_service, user_repo, role_repo, user_role_repo, clock, uow
        )

        with pytest.raises(RoleNotFoundError):
            use_case.execute(
                RemoveRoleCommand(actor_id="admin", target_user_id="u1", role_key="nope")
            )

    def test_remove_role_unknown_user_raises(
        self, authorization_service, user_repo, role_repo, user_role_repo, clock, uow
    ):
        authorization_service.grant("admin", "user.remove_role")
        use_case = build_use_case(
            authorization_service, user_repo, role_repo, user_role_repo, clock, uow
        )

        with pytest.raises(UserNotFoundError):
            use_case.execute(
                RemoveRoleCommand(actor_id="admin", target_user_id="ghost", role_key="admin")
            )
