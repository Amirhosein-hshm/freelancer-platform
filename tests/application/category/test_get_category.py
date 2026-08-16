import pytest

from app.application.category.dto import GetCategoryQuery
from app.application.category.use_cases.get_category import GetCategoryUseCase
from app.domain.category.exceptions import CategoryNotFoundError


class TestGetCategoryUseCase:
    def build(self, category_repo):
        return GetCategoryUseCase(category_repo=category_repo)

    async def test_get_category_returns_details(
        self, category_repo, make_category
    ):
        await make_category(
            category_id="cat-1",
            name="Web Development",
            description="Web projects",
            parent_category_id="cat-parent",
        )
        use_case = self.build(category_repo)

        result = await use_case.execute(GetCategoryQuery(category_id="cat-1"))

        assert result.category_id == "cat-1"
        assert result.name == "Web Development"
        assert result.description == "Web projects"
        assert result.parent_category_id == "cat-parent"

    async def test_get_unknown_category_raises(self, category_repo):
        use_case = self.build(category_repo)

        with pytest.raises(CategoryNotFoundError):
            await use_case.execute(GetCategoryQuery(category_id="ghost"))
