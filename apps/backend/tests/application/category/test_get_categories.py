from app.application.category.dto import GetCategoriesQuery
from app.application.category.use_cases.get_categories import GetCategoriesUseCase


class TestGetCategoriesUseCase:
    async def test_returns_only_active_categories(self, category_repo, make_category):
        await make_category(category_id="cat-1", slug="a")
        await make_category(category_id="cat-2", slug="b", is_active=False)
        use_case = GetCategoriesUseCase(category_repo)

        result = await use_case.execute(GetCategoriesQuery())

        assert [c.slug for c in result.categories] == ["a"]

    async def test_returns_empty_when_no_categories(self, category_repo):
        use_case = GetCategoriesUseCase(category_repo)

        result = await use_case.execute(GetCategoriesQuery())

        assert result.categories == []
