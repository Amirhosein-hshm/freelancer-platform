import pytest

from app.application.iam.dto import RevokePermissionCommand
from app.application.iam.use_cases.revoke_permission import RevokePermissionUseCase
from app.application.shared.exceptions import PermissionDeniedError


def build_use_case(authorization_service, role_permission_repo, uow) -> RevokePermissionUseCase:
    return RevokePermissionUseCase(
        authorization_service=authorization_service,
        role_permission_repo=role_permission_repo,
        uow=uow,
    )


class TestRevokePermissionUseCase:
    def test_revoke_permission_success(self, authorization_service, role_permission_repo, uow):
        authorization_service.grant("admin", "user.revoke_permission")
        use_case = build_use_case(authorization_service, role_permission_repo, uow)

        result = use_case.execute(
            RevokePermissionCommand(actor_id="admin", role_id="role-customer", permission_id="perm-1")
        )

        assert result.role_id == "role-customer"
        assert result.permission_id == "perm-1"
        assert uow.committed is True

    def test_revoke_permission_requires_permission(self, authorization_service, role_permission_repo, uow):
        use_case = build_use_case(authorization_service, role_permission_repo, uow)

        with pytest.raises(PermissionDeniedError):
            use_case.execute(
                RevokePermissionCommand(actor_id="admin", role_id="role-customer", permission_id="perm-1")
            )
