import pytest

from app.application.iam.dto import AdminListUsersQuery
from app.application.iam.use_cases.admin_list_users import AdminListUsersUseCase
from app.application.shared.exceptions import PermissionDeniedError
from app.domain.iam.enums import UserStatus


class TestAdminListUsersUseCase:
    def build(self, authorization_service, user_repo):
        return AdminListUsersUseCase(
            authorization_service=authorization_service,
            user_repo=user_repo,
        )

    async def test_list_users_requires_permission(self, authorization_service, user_repo, make_user):
        await make_user(user_id="u1")
        use_case = self.build(authorization_service, user_repo)

        with pytest.raises(PermissionDeniedError):
            await use_case.execute(AdminListUsersQuery(actor_id="admin"))

    async def test_unfiltered_list_returns_all_with_total(self, authorization_service, user_repo, make_user):
        authorization_service.grant("admin", "user.read")
        await make_user(user_id="u1")
        await make_user(user_id="u2")
        await make_user(user_id="u3")
        use_case = self.build(authorization_service, user_repo)

        result = await use_case.execute(AdminListUsersQuery(actor_id="admin", page=1, page_size=2))

        assert [u.user_id for u in result.users] == ["u1", "u2"]
        assert result.total_items == 3
        assert result.page == 1
        assert result.page_size == 2

    async def test_unfiltered_list_second_page(self, authorization_service, user_repo, make_user):
        authorization_service.grant("admin", "user.read")
        await make_user(user_id="u1")
        await make_user(user_id="u2")
        await make_user(user_id="u3")
        use_case = self.build(authorization_service, user_repo)

        result = await use_case.execute(AdminListUsersQuery(actor_id="admin", page=2, page_size=2))

        assert [u.user_id for u in result.users] == ["u3"]
        assert result.total_items == 3

    async def test_status_filter_returns_matching_users_only(self, authorization_service, user_repo, make_user):
        authorization_service.grant("admin", "user.read")
        await make_user(user_id="u1")
        await make_user(user_id="u2")
        await make_user(user_id="u3", status=UserStatus.BLOCKED)
        use_case = self.build(authorization_service, user_repo)

        result = await use_case.execute(AdminListUsersQuery(actor_id="admin", status=UserStatus.BLOCKED))

        assert [u.user_id for u in result.users] == ["u3"]
        assert result.total_items == 1
        assert result.users[0].status == "blocked"

    async def test_status_filter_respects_pagination_and_ignores_other_statuses(
        self, authorization_service, user_repo, make_user
    ):
        authorization_service.grant("admin", "user.read")
        await make_user(user_id="u1")
        await make_user(user_id="u2")
        await make_user(user_id="u3")
        await make_user(user_id="u4")
        use_case = self.build(authorization_service, user_repo)

        result = await use_case.execute(
            AdminListUsersQuery(actor_id="admin", status=UserStatus.ACTIVE, page=2, page_size=2)
        )

        assert [u.user_id for u in result.users] == ["u3", "u4"]
        assert result.total_items == 4
