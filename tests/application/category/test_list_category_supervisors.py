from datetime import UTC, datetime

import pytest

from app.application.category.dto import ListCategorySupervisorsQuery
from app.application.category.use_cases.list_category_supervisors import (
    ListCategorySupervisorsUseCase,
)
from app.domain.category.entities import CategorySupervisor
from app.domain.category.exceptions import CategoryNotFoundError

NOW = datetime(2026, 8, 2, tzinfo=UTC)


class TestListCategorySupervisorsUseCase:
    def build(self, category_repo, category_supervisor_repo):
        return ListCategorySupervisorsUseCase(
            category_repo=category_repo,
            supervisor_repo=category_supervisor_repo,
        )

    async def test_list_supervisors_returns_active_links(
        self,
        category_repo,
        category_supervisor_repo,
        make_category,
    ):
        await make_category(category_id="cat-1")
        supervisor = CategorySupervisor(
            id="link-1",
            category_id="cat-1",
            supervisor_user_id="sup-1",
            assigned_by_user_id="admin-1",
            is_primary=True,
            is_active=True,
            assigned_at=NOW,
            created_at=NOW,
        )
        await category_supervisor_repo.add(supervisor)
        use_case = self.build(category_repo, category_supervisor_repo)

        result = await use_case.execute(
            ListCategorySupervisorsQuery(category_id="cat-1")
        )

        assert len(result.supervisors) == 1
        assert result.supervisors[0].supervisor_user_id == "sup-1"
        assert result.supervisors[0].is_primary is True

    async def test_list_supervisors_unknown_category_raises(
        self, category_repo, category_supervisor_repo
    ):
        use_case = self.build(category_repo, category_supervisor_repo)

        with pytest.raises(CategoryNotFoundError):
            await use_case.execute(
                ListCategorySupervisorsQuery(category_id="ghost")
            )
