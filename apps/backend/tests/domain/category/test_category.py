from datetime import UTC, datetime

from app.domain.category.entities import Category

NOW = datetime(2026, 8, 2, tzinfo=UTC)


def make_category(**overrides: object) -> Category:
    defaults: dict[str, object] = {
        "id": "cat-1",
        "parent_category_id": None,
        "category_key": "webdev",
        "name": "Web Development",
        "slug": "web-development",
        "description": None,
        "is_active": True,
        "sort_order": 0,
        "created_at": NOW,
    }
    defaults.update(overrides)
    return Category(**defaults)  # type: ignore[arg-type]


class TestCategory:
    def test_deactivate_sets_inactive(self):
        category = make_category()
        category.deactivate()
        assert category.is_active is False

    def test_rename_updates_name_and_slug(self):
        category = make_category()
        category.rename("Mobile", "mobile")
        assert category.name == "Mobile"
        assert category.slug == "mobile"

    def test_soft_delete_sets_deleted_at_and_inactive(self):
        category = make_category()
        category.soft_delete(NOW)
        assert category.deleted_at == NOW
        assert category.is_active is False
