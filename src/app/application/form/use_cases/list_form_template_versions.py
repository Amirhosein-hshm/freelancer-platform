from dataclasses import dataclass

from app.application.form.dto import FormTemplateResult
from app.application.form.use_cases.get_form_template import to_template_result
from app.application.shared.use_case import UseCase
from app.domain.form.repositories import IFormTemplateRepository
from app.domain.shared.types import EntityId


@dataclass(frozen=True)
class ListFormTemplateVersionsQuery:
    template_id: EntityId


@dataclass(frozen=True)
class ListFormTemplateVersionsResult:
    versions: list[FormTemplateResult]


class ListFormTemplateVersionsUseCase(
    UseCase[ListFormTemplateVersionsQuery, ListFormTemplateVersionsResult]
):
    def __init__(self, template_repo: IFormTemplateRepository) -> None:
        self._template_repo = template_repo

    async def execute(
        self, request: ListFormTemplateVersionsQuery
    ) -> ListFormTemplateVersionsResult:
        template = await self._template_repo.get_by_id(request.template_id)
        versions = await self._template_repo.list_versions(
            template.category_id, template.template_key
        )
        return ListFormTemplateVersionsResult(
            versions=[to_template_result(t) for t in versions]
        )
