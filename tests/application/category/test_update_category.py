import pytest

from app.application.category.dto import UpdateCategoryCommand
from app.application.category.use_cases.update_category import UpdateCategoryUseCase
from app.application.shared.exceptions import ValidationError
from app.domain.category.exceptions import CategoryNotFoundError, DuplicateCategorySlugError


def build_use_case(category_repo, uow) -> UpdateCategoryUseCase:
    return UpdateCategoryUseCase(category_repo=category_repo, uow=uow)


class TestUpdateCategoryUseCase:
    def test_update_category_succeeds(self, category_repo, uow, make_category):
        make_category(category_id="cat-1", slug="old-slug")
        use_case = build_use_case(category_repo, uow)

        result = use_case.execute(
            UpdateCategoryCommand(category_id="cat-1", name="New Name", slug="new-slug")
        )

        assert result.name == "New Name"
        assert result.slug == "new-slug"
        assert category_repo.get_by_id("cat-1").name == "New Name"

    def test_update_duplicate_slug_raises(self, category_repo, uow, make_category):
        make_category(category_id="cat-1", slug="cat-one")
        make_category(category_id="cat-2", slug="taken")
        use_case = build_use_case(category_repo, uow)

        with pytest.raises(DuplicateCategorySlugError):
            use_case.execute(UpdateCategoryCommand(category_id="cat-1", name="X", slug="taken"))

    def test_update_unknown_category_raises(self, category_repo, uow):
        use_case = build_use_case(category_repo, uow)

        with pytest.raises(CategoryNotFoundError):
            use_case.execute(UpdateCategoryCommand(category_id="ghost", name="X", slug="x"))

    def test_update_missing_fields_raises_validation(self, category_repo, uow, make_category):
        make_category(category_id="cat-1")
        use_case = build_use_case(category_repo, uow)

        with pytest.raises(ValidationError):
            use_case.execute(UpdateCategoryCommand(category_id="cat-1", name="", slug=""))
