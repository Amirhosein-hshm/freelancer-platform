import pytest

from app.application.iam.dto import ActivateUserCommand, BlockUserCommand
from app.application.iam.use_cases.activate_user import ActivateUserUseCase
from app.application.iam.use_cases.block_user import BlockUserUseCase
from app.application.shared.exceptions import PermissionDeniedError
from app.domain.iam.enums import UserStatus
from app.domain.iam.exceptions import UserNotFoundError


class TestBlockUserUseCase:
    def build(self, authorization_service, user_repo, clock, uow) -> BlockUserUseCase:
        return BlockUserUseCase(
            authorization_service=authorization_service,
            user_repo=user_repo,
            clock=clock,
            uow=uow,
        )

    def test_block_requires_permission(self, authorization_service, user_repo, clock, uow, make_user):
        make_user(user_id="u1", status=UserStatus.ACTIVE)
        use_case = self.build(authorization_service, user_repo, clock, uow)

        with pytest.raises(PermissionDeniedError):
            use_case.execute(BlockUserCommand(actor_id="admin", target_user_id="u1", reason="abuse"))

    def test_block_succeeds_with_permission(
        self, authorization_service, user_repo, clock, uow, make_user
    ):
        authorization_service.grant("admin", "user.block")
        make_user(user_id="u1", status=UserStatus.ACTIVE)
        use_case = self.build(authorization_service, user_repo, clock, uow)

        result = use_case.execute(
            BlockUserCommand(actor_id="admin", target_user_id="u1", reason="abuse")
        )

        assert result.status == UserStatus.BLOCKED.value
        assert user_repo.get_by_id("u1").status == UserStatus.BLOCKED

    def test_block_unknown_user_raises(
        self, authorization_service, user_repo, clock, uow
    ):
        authorization_service.grant("admin", "user.block")
        use_case = self.build(authorization_service, user_repo, clock, uow)

        with pytest.raises(UserNotFoundError):
            use_case.execute(BlockUserCommand(actor_id="admin", target_user_id="ghost", reason="x"))


class TestActivateUserUseCase:
    def build(self, authorization_service, user_repo, clock, uow) -> ActivateUserUseCase:
        return ActivateUserUseCase(
            authorization_service=authorization_service,
            user_repo=user_repo,
            clock=clock,
            uow=uow,
        )

    def test_activate_requires_permission(self, authorization_service, user_repo, clock, uow, make_user):
        make_user(user_id="u1", status=UserStatus.BLOCKED)
        use_case = self.build(authorization_service, user_repo, clock, uow)

        with pytest.raises(PermissionDeniedError):
            use_case.execute(ActivateUserCommand(actor_id="admin", target_user_id="u1"))

    def test_activate_succeeds_with_permission(
        self, authorization_service, user_repo, clock, uow, make_user
    ):
        authorization_service.grant("admin", "user.activate")
        make_user(user_id="u1", status=UserStatus.BLOCKED)
        use_case = self.build(authorization_service, user_repo, clock, uow)

        result = use_case.execute(ActivateUserCommand(actor_id="admin", target_user_id="u1"))

        assert result.status == UserStatus.ACTIVE.value
        assert user_repo.get_by_id("u1").status == UserStatus.ACTIVE

    def test_activate_unknown_user_raises(self, authorization_service, user_repo, clock, uow):
        authorization_service.grant("admin", "user.activate")
        use_case = self.build(authorization_service, user_repo, clock, uow)

        with pytest.raises(UserNotFoundError):
            use_case.execute(ActivateUserCommand(actor_id="admin", target_user_id="ghost"))
