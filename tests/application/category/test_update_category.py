import pytest

from app.application.category.dto import UpdateCategoryCommand
from app.application.category.use_cases.update_category import UpdateCategoryUseCase
from app.application.shared.exceptions import ValidationError
from app.domain.category.exceptions import CategoryNotFoundError, DuplicateCategorySlugError


def build_use_case(authorization_service, category_repo, uow) -> UpdateCategoryUseCase:
    return UpdateCategoryUseCase(
        authorization_service=authorization_service, category_repo=category_repo, uow=uow
    )


class TestUpdateCategoryUseCase:
    async def test_update_category_succeeds(self, authorization_service, category_repo, uow, make_category):
        authorization_service.grant("admin", "category.manage")
        await make_category(category_id="cat-1", slug="old-slug")
        use_case = build_use_case(authorization_service, category_repo, uow)

        result = await use_case.execute(
            UpdateCategoryCommand(
                actor_id="admin", category_id="cat-1", name="New Name", slug="new-slug"
            )
        )

        assert result.name == "New Name"
        assert result.slug == "new-slug"
        assert (await category_repo.get_by_id("cat-1")).name == "New Name"

    async def test_update_duplicate_slug_raises(
        self, authorization_service, category_repo, uow, make_category
    ):
        authorization_service.grant("admin", "category.manage")
        await make_category(category_id="cat-1", slug="cat-one")
        await make_category(category_id="cat-2", slug="taken")
        use_case = build_use_case(authorization_service, category_repo, uow)

        with pytest.raises(DuplicateCategorySlugError):
            await use_case.execute(
                UpdateCategoryCommand(actor_id="admin", category_id="cat-1", name="X", slug="taken")
            )

    async def test_update_unknown_category_raises(self, authorization_service, category_repo, uow):
        authorization_service.grant("admin", "category.manage")
        use_case = build_use_case(authorization_service, category_repo, uow)

        with pytest.raises(CategoryNotFoundError):
            await use_case.execute(
                UpdateCategoryCommand(actor_id="admin", category_id="ghost", name="X", slug="x")
            )

    async def test_update_missing_fields_raises_validation(
        self, authorization_service, category_repo, uow, make_category
    ):
        authorization_service.grant("admin", "category.manage")
        await make_category(category_id="cat-1")
        use_case = build_use_case(authorization_service, category_repo, uow)

        with pytest.raises(ValidationError):
            await use_case.execute(
                UpdateCategoryCommand(actor_id="admin", category_id="cat-1", name="", slug="")
            )
