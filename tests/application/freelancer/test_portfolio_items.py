import pytest

from app.application.freelancer.dto import (
    AddPortfolioItemCommand,
    DeletePortfolioItemCommand,
    UpdatePortfolioItemCommand,
)
from app.application.freelancer.use_cases.add_portfolio_item import AddPortfolioItemUseCase
from app.application.freelancer.use_cases.delete_portfolio_item import DeletePortfolioItemUseCase
from app.application.freelancer.use_cases.update_portfolio_item import UpdatePortfolioItemUseCase
from app.application.shared.exceptions import ValidationError
from app.domain.freelancer.exceptions import PortfolioItemNotFoundError


class TestAddPortfolioItemUseCase:
    async def test_add_item_succeeds(
        self, profile_repo, portfolio_item_repo, id_generator, clock, uow, make_profile
    ):
        await make_profile(user_id="user-1")
        use_case = AddPortfolioItemUseCase(
            profile_repo=profile_repo,
            portfolio_item_repo=portfolio_item_repo,
            id_generator=id_generator,
            clock=clock,
            uow=uow,
        )

        result = await use_case.execute(
            AddPortfolioItemCommand(user_id="user-1", title="My Project", is_featured=True)
        )

        item = await portfolio_item_repo.get_by_id(result.item_id)
        assert item.freelancer_profile_id == "profile-1"
        assert item.title == "My Project"
        assert item.is_featured is True
        assert uow.committed is True

    async def test_empty_title_raises_validation(
        self, profile_repo, portfolio_item_repo, id_generator, clock, uow, make_profile
    ):
        await make_profile(user_id="user-1")
        use_case = AddPortfolioItemUseCase(
            profile_repo=profile_repo,
            portfolio_item_repo=portfolio_item_repo,
            id_generator=id_generator,
            clock=clock,
            uow=uow,
        )

        with pytest.raises(ValidationError):
            await use_case.execute(AddPortfolioItemCommand(user_id="user-1", title="  "))


class TestUpdatePortfolioItemUseCase:
    async def test_update_item_succeeds(self, profile_repo, portfolio_item_repo, make_profile, make_portfolio_item):
        await make_profile(user_id="user-1")
        await make_portfolio_item()
        use_case = UpdatePortfolioItemUseCase(
            profile_repo=profile_repo, portfolio_item_repo=portfolio_item_repo
        )

        result = await use_case.execute(
            UpdatePortfolioItemCommand(user_id="user-1", item_id="item-1", title="New Title")
        )

        assert result.item_id == "item-1"
        assert (await portfolio_item_repo.get_by_id("item-1")).title == "New Title"

    async def test_update_unknown_item_raises(self, profile_repo, portfolio_item_repo, make_profile):
        await make_profile(user_id="user-1")
        use_case = UpdatePortfolioItemUseCase(
            profile_repo=profile_repo, portfolio_item_repo=portfolio_item_repo
        )

        with pytest.raises(PortfolioItemNotFoundError):
            await use_case.execute(
                UpdatePortfolioItemCommand(user_id="user-1", item_id="ghost", title="X")
            )

    async def test_update_item_of_another_profile_raises(
        self, profile_repo, portfolio_item_repo, make_profile, make_portfolio_item
    ):
        await make_profile(user_id="user-1", profile_id="profile-1")
        await make_profile(user_id="user-2", profile_id="profile-2")
        await make_portfolio_item(profile_id="profile-2")
        use_case = UpdatePortfolioItemUseCase(
            profile_repo=profile_repo, portfolio_item_repo=portfolio_item_repo
        )

        with pytest.raises(PortfolioItemNotFoundError):
            await use_case.execute(
                UpdatePortfolioItemCommand(user_id="user-1", item_id="item-1", title="X")
            )


class TestDeletePortfolioItemUseCase:
    async def test_delete_item_succeeds(
        self, profile_repo, portfolio_item_repo, make_profile, make_portfolio_item
    ):
        await make_profile(user_id="user-1")
        await make_portfolio_item()
        use_case = DeletePortfolioItemUseCase(
            profile_repo=profile_repo, portfolio_item_repo=portfolio_item_repo
        )

        result = await use_case.execute(DeletePortfolioItemCommand(user_id="user-1", item_id="item-1"))

        assert result.item_id == "item-1"
        with pytest.raises(PortfolioItemNotFoundError):
            await portfolio_item_repo.get_by_id("item-1")

    async def test_delete_item_of_another_profile_raises(
        self, profile_repo, portfolio_item_repo, make_profile, make_portfolio_item
    ):
        await make_profile(user_id="user-1", profile_id="profile-1")
        await make_profile(user_id="user-2", profile_id="profile-2")
        await make_portfolio_item(profile_id="profile-2")
        use_case = DeletePortfolioItemUseCase(
            profile_repo=profile_repo, portfolio_item_repo=portfolio_item_repo
        )

        with pytest.raises(PortfolioItemNotFoundError):
            await use_case.execute(DeletePortfolioItemCommand(user_id="user-1", item_id="item-1"))
