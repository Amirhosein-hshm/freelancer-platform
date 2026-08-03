from datetime import UTC, datetime

import pytest

from app.application.iam.dto import GrantPermissionCommand
from app.application.iam.use_cases.grant_permission import GrantPermissionUseCase
from app.application.shared.exceptions import PermissionDeniedError
from app.domain.iam.entities import Permission
from app.domain.iam.exceptions import (
    PermissionAlreadyGrantedError,
    PermissionNotFoundError,
    RoleNotFoundError,
)

NOW = datetime(2026, 8, 2, tzinfo=UTC)


def build_use_case(
    authorization_service,
    role_repo,
    permission_repo,
    role_permission_repo,
    id_generator,
    clock,
    uow,
) -> GrantPermissionUseCase:
    return GrantPermissionUseCase(
        authorization_service=authorization_service,
        role_repo=role_repo,
        permission_repo=permission_repo,
        role_permission_repo=role_permission_repo,
        id_generator=id_generator,
        clock=clock,
        uow=uow,
    )


class TestGrantPermissionUseCase:
    def test_grant_permission_success(
        self,
        authorization_service,
        role_repo,
        permission_repo,
        role_permission_repo,
        id_generator,
        clock,
        uow,
    ):
        authorization_service.grant("admin", "user.grant_permission")
        permission_repo.add(
            Permission(
                id="perm-1",
                permission_key="project.create",
                module="project",
                action="create",
                created_at=NOW,
            )
        )
        use_case = build_use_case(
            authorization_service, role_repo, permission_repo, role_permission_repo,
            id_generator, clock, uow,
        )

        result = use_case.execute(
            GrantPermissionCommand(actor_id="admin", role_id="role-customer", permission_id="perm-1")
        )

        assert result.permission_id == "perm-1"
        granted = role_permission_repo.list_permissions_for_role("role-customer")
        assert any(p.id == "perm-1" for p in granted)

    def test_grant_permission_requires_permission(
        self,
        authorization_service,
        role_repo,
        permission_repo,
        role_permission_repo,
        id_generator,
        clock,
        uow,
    ):
        use_case = build_use_case(
            authorization_service, role_repo, permission_repo, role_permission_repo,
            id_generator, clock, uow,
        )

        with pytest.raises(PermissionDeniedError):
            use_case.execute(
                GrantPermissionCommand(actor_id="admin", role_id="role-customer", permission_id="perm-1")
            )

    def test_grant_permission_already_granted_raises(
        self,
        authorization_service,
        role_repo,
        permission_repo,
        role_permission_repo,
        id_generator,
        clock,
        uow,
    ):
        authorization_service.grant("admin", "user.grant_permission")
        permission_repo.add(
            Permission(
                id="perm-1", permission_key="x", module="m", action="a", created_at=NOW
            )
        )
        use_case = build_use_case(
            authorization_service, role_repo, permission_repo, role_permission_repo,
            id_generator, clock, uow,
        )

        use_case.execute(
            GrantPermissionCommand(actor_id="admin", role_id="role-customer", permission_id="perm-1")
        )

        with pytest.raises(PermissionAlreadyGrantedError):
            use_case.execute(
                GrantPermissionCommand(actor_id="admin", role_id="role-customer", permission_id="perm-1")
            )

    def test_grant_permission_unknown_role_raises(
        self,
        authorization_service,
        role_repo,
        permission_repo,
        role_permission_repo,
        id_generator,
        clock,
        uow,
    ):
        authorization_service.grant("admin", "user.grant_permission")
        permission_repo.add(
            Permission(
                id="perm-1", permission_key="x", module="m", action="a", created_at=NOW
            )
        )
        use_case = build_use_case(
            authorization_service, role_repo, permission_repo, role_permission_repo,
            id_generator, clock, uow,
        )

        with pytest.raises(RoleNotFoundError):
            use_case.execute(
                GrantPermissionCommand(actor_id="admin", role_id="ghost-role", permission_id="perm-1")
            )

    def test_grant_permission_unknown_permission_raises(
        self,
        authorization_service,
        role_repo,
        permission_repo,
        role_permission_repo,
        id_generator,
        clock,
        uow,
    ):
        authorization_service.grant("admin", "user.grant_permission")
        use_case = build_use_case(
            authorization_service, role_repo, permission_repo, role_permission_repo,
            id_generator, clock, uow,
        )

        with pytest.raises(PermissionNotFoundError):
            use_case.execute(
                GrantPermissionCommand(actor_id="admin", role_id="role-customer", permission_id="ghost")
            )
