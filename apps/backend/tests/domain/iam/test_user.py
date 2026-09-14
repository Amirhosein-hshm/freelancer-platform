from datetime import UTC, datetime

import pytest

from app.domain.iam.entities import User
from app.domain.iam.enums import UserStatus
from app.domain.iam.exceptions import (
    InvalidStateTransitionError,
    UserAlreadyBlockedError,
)
from app.domain.iam.value_objects import Email, PasswordHash

NOW = datetime(2026, 8, 2, tzinfo=UTC)


def make_user(**overrides: object) -> User:
    defaults: dict[str, object] = {
        "id": "user-1",
        "email": Email("user@example.com"),
        "phone": None,
        "password_hash": PasswordHash("hash"),
        "first_name": "John",
        "last_name": "Doe",
        "status": UserStatus.PENDING,
        "created_at": NOW,
    }
    defaults.update(overrides)
    return User(**defaults)  # type: ignore[arg-type]


class TestUserActivate:
    def test_activate_from_pending_succeeds(self):
        user = make_user(status=UserStatus.PENDING)
        user.activate()
        assert user.status == UserStatus.ACTIVE

    def test_activate_from_blocked_succeeds(self):
        user = make_user(status=UserStatus.BLOCKED)
        user.activate()
        assert user.status == UserStatus.ACTIVE

    def test_activate_when_already_active_is_noop(self):
        user = make_user(status=UserStatus.ACTIVE)
        user.activate()
        assert user.status == UserStatus.ACTIVE

    def test_activate_from_archived_raises(self):
        user = make_user(status=UserStatus.ARCHIVED)
        with pytest.raises(InvalidStateTransitionError):
            user.activate()


class TestUserBlock:
    def test_block_from_active_succeeds(self):
        user = make_user(status=UserStatus.ACTIVE)
        user.block("abuse")
        assert user.status == UserStatus.BLOCKED

    def test_block_from_pending_succeeds(self):
        user = make_user(status=UserStatus.PENDING)
        user.block("spam")
        assert user.status == UserStatus.BLOCKED

    def test_block_when_already_blocked_raises(self):
        user = make_user(status=UserStatus.BLOCKED)
        with pytest.raises(UserAlreadyBlockedError):
            user.block("again")

    def test_block_from_archived_raises(self):
        user = make_user(status=UserStatus.ARCHIVED)
        with pytest.raises(InvalidStateTransitionError):
            user.block("late")


class TestUserLifecycle:
    def test_record_login_sets_last_login_at(self):
        user = make_user()
        user.record_login(NOW)
        assert user.last_login_at == NOW

    def test_change_password_updates_hash_and_timestamp(self):
        user = make_user()
        new_hash = PasswordHash("new-hash")
        user.change_password(new_hash, NOW)
        assert user.password_hash == new_hash
        assert user.password_changed_at == NOW

    def test_soft_delete_sets_deleted_at(self):
        user = make_user()
        user.soft_delete(NOW)
        assert user.deleted_at == NOW


class TestUserIsActive:
    def test_active_user_is_active(self):
        assert make_user(status=UserStatus.ACTIVE).is_active() is True

    def test_pending_user_is_not_active(self):
        assert make_user(status=UserStatus.PENDING).is_active() is False

    def test_blocked_user_is_not_active(self):
        assert make_user(status=UserStatus.BLOCKED).is_active() is False

    def test_deleted_user_is_not_active(self):
        user = make_user(status=UserStatus.ACTIVE, deleted_at=NOW)
        assert user.is_active() is False
