from datetime import UTC, datetime

import pytest

from app.domain.category.entities import Category
from tests.fakes.fake_category_repository import FakeCategoryRepository
from tests.fakes.fake_category_supervisor_repository import FakeCategorySupervisorRepository

NOW = datetime(2026, 8, 2, tzinfo=UTC)


@pytest.fixture
def category_repo() -> FakeCategoryRepository:
    return FakeCategoryRepository()


@pytest.fixture
def category_supervisor_repo() -> FakeCategorySupervisorRepository:
    return FakeCategorySupervisorRepository()


@pytest.fixture
def make_category(category_repo: FakeCategoryRepository):
    def _make(category_id: str = "cat-1", slug: str = "web-development", **overrides: object) -> Category:
        fields: dict[str, object] = {
            "id": category_id,
            "parent_category_id": None,
            "category_key": "webdev",
            "name": "Web Development",
            "slug": slug,
            "description": None,
            "is_active": True,
            "sort_order": 0,
            "created_at": NOW,
        }
        fields.update(overrides)
        category = Category(**fields)  # type: ignore[arg-type]
        category_repo.add(category)
        return category

    return _make
