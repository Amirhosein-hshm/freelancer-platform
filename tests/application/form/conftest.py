from datetime import UTC, datetime

import pytest

from app.domain.form.entities import FormTemplate
from app.domain.form.enums import FormTemplateStatus
from tests.fakes.fake_form_template_repository import FakeFormTemplateRepository

NOW = datetime(2026, 8, 2, tzinfo=UTC)


@pytest.fixture
def template_repo() -> FakeFormTemplateRepository:
    return FakeFormTemplateRepository()


@pytest.fixture
def make_template(template_repo: FakeFormTemplateRepository):
    def _make(
        template_id: str = "template-1",
        category_id: str = "cat-1",
        **overrides: object,
    ) -> FormTemplate:
        fields: dict[str, object] = {
            "id": template_id,
            "category_id": category_id,
            "template_key": "project-form",
            "name": "Project Form",
            "version_no": 1,
            "status": FormTemplateStatus.DRAFT,
            "is_active": True,
            "published_by_user_id": None,
            "published_at": None,
            "fields": [],
            "deleted_at": None,
            "created_at": NOW,
        }
        fields.update(overrides)
        template = FormTemplate(**fields)  # type: ignore[arg-type]
        template_repo.add(template)
        return template

    return _make
