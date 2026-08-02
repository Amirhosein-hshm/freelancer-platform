from datetime import UTC, datetime

import pytest

from app.domain.iam.entities import UserRole
from app.domain.iam.exceptions import InvalidStateTransitionError

NOW = datetime(2026, 8, 2, tzinfo=UTC)


def make_user_role(**overrides: object) -> UserRole:
    defaults: dict[str, object] = {
        "id": "ur-1",
        "user_id": "user-1",
        "role_id": "role-1",
        "assigned_by_user_id": "admin-1",
        "assigned_at": NOW,
        "revoked_at": None,
        "is_active": True,
        "created_at": NOW,
    }
    defaults.update(overrides)
    return UserRole(**defaults)  # type: ignore[arg-type]


class TestUserRoleRevoke:
    def test_revoke_marks_inactive(self):
        user_role = make_user_role()
        user_role.revoke(NOW)
        assert user_role.is_active is False
        assert user_role.revoked_at == NOW

    def test_revoke_already_revoked_raises(self):
        user_role = make_user_role(is_active=False, revoked_at=NOW)
        with pytest.raises(InvalidStateTransitionError):
            user_role.revoke(NOW)
