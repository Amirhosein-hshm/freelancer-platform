import pytest

from app.application.iam.dto import ChangePasswordCommand
from app.application.iam.use_cases.change_password import ChangePasswordUseCase
from app.application.shared.exceptions import ValidationError
from app.domain.iam.exceptions import InvalidCredentialsError, UserNotFoundError


def build_use_case(user_repo, password_hasher, clock, uow) -> ChangePasswordUseCase:
    return ChangePasswordUseCase(
        user_repo=user_repo, password_hasher=password_hasher, clock=clock, uow=uow
    )


class TestChangePasswordUseCase:
    def test_change_password_succeeds(self, user_repo, password_hasher, clock, uow, make_user):
        make_user(user_id="u1", password="old-pass")
        use_case = build_use_case(user_repo, password_hasher, clock, uow)

        result = use_case.execute(
            ChangePasswordCommand(user_id="u1", old_password="old-pass", new_password="new-pass")
        )

        assert result.user_id == "u1"
        assert result.password_changed_at == clock.now()
        updated = user_repo.get_by_id("u1")
        assert password_hasher.verify("new-pass", updated.password_hash.value)

    def test_change_password_wrong_old_password_raises(
        self, user_repo, password_hasher, clock, uow, make_user
    ):
        make_user(user_id="u1", password="real-pass")
        use_case = build_use_case(user_repo, password_hasher, clock, uow)

        with pytest.raises(InvalidCredentialsError):
            use_case.execute(
                ChangePasswordCommand(user_id="u1", old_password="nope", new_password="new-pass")
            )

    def test_change_password_unknown_user_raises(self, user_repo, password_hasher, clock, uow):
        use_case = build_use_case(user_repo, password_hasher, clock, uow)

        with pytest.raises(UserNotFoundError):
            use_case.execute(
                ChangePasswordCommand(user_id="ghost", old_password="x", new_password="y")
            )

    def test_change_password_missing_fields_raises_validation(
        self, user_repo, password_hasher, clock, uow, make_user
    ):
        make_user(user_id="u1")
        use_case = build_use_case(user_repo, password_hasher, clock, uow)

        with pytest.raises(ValidationError):
            use_case.execute(ChangePasswordCommand(user_id="u1", old_password="", new_password=""))
