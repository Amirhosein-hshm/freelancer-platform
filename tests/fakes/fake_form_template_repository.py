from app.domain.form.entities import FormTemplate
from app.domain.form.enums import FormTemplateStatus
from app.domain.form.exceptions import FormTemplateNotFoundError
from app.domain.form.repositories import IFormTemplateRepository
from app.domain.shared.types import EntityId


class FakeFormTemplateRepository(IFormTemplateRepository):
    def __init__(self) -> None:
        self._store: dict[str, FormTemplate] = {}

    async def add(self, template: FormTemplate) -> None:
        self._store[template.id] = template

    async def get_by_id(self, template_id: EntityId) -> FormTemplate:
        try:
            return self._store[template_id]
        except KeyError:
            raise FormTemplateNotFoundError(f"Form template {template_id} not found.") from None

    async def get_published_for_category(self, category_id: EntityId) -> FormTemplate:
        published = [
            t
            for t in self._store.values()
            if t.category_id == category_id
            and t.status == FormTemplateStatus.PUBLISHED
            and t.deleted_at is None
        ]
        if not published:
            raise FormTemplateNotFoundError(
                f"No published form template for category {category_id}."
            )
        return max(published, key=lambda t: t.version_no)

    async def update(self, template: FormTemplate) -> None:
        self._store[template.id] = template

    async def delete(self, template_id: EntityId) -> None:
        self._store.pop(template_id, None)

    async def list_versions(
        self, category_id: EntityId, template_key: str
    ) -> list[FormTemplate]:
        return [
            t
            for t in self._store.values()
            if t.category_id == category_id and t.template_key == template_key
        ]
