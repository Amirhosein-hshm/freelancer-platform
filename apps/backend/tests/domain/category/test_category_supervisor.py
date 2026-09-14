from datetime import UTC, datetime

import pytest

from app.domain.category.entities import CategorySupervisor
from app.domain.shared.exceptions import InvalidStateTransitionError

NOW = datetime(2026, 8, 2, tzinfo=UTC)


def make_link(**overrides: object) -> CategorySupervisor:
    defaults: dict[str, object] = {
        "id": "link-1",
        "category_id": "cat-1",
        "supervisor_user_id": "user-1",
        "assigned_by_user_id": "admin-1",
        "is_primary": True,
        "is_active": True,
        "assigned_at": NOW,
        "created_at": NOW,
    }
    defaults.update(overrides)
    return CategorySupervisor(**defaults)  # type: ignore[arg-type]


class TestCategorySupervisor:
    def test_revoke_marks_inactive(self):
        link = make_link()
        link.revoke(NOW)
        assert link.is_active is False
        assert link.revoked_at == NOW

    def test_revoke_already_revoked_raises(self):
        link = make_link(is_active=False, revoked_at=NOW)
        with pytest.raises(InvalidStateTransitionError):
            link.revoke(NOW)
