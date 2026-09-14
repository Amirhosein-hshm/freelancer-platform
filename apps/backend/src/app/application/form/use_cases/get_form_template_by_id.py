from dataclasses import dataclass

from app.application.form.dto import FormTemplateResult
from app.application.form.use_cases.get_form_template import to_template_result
from app.application.shared.use_case import UseCase
from app.domain.form.repositories import IFormTemplateRepository
from app.domain.shared.types import EntityId


@dataclass(frozen=True)
class GetFormTemplateByIdQuery:
    template_id: EntityId


class GetFormTemplateByIdUseCase(UseCase[GetFormTemplateByIdQuery, FormTemplateResult]):
    def __init__(self, template_repo: IFormTemplateRepository) -> None:
        self._template_repo = template_repo

    async def execute(self, request: GetFormTemplateByIdQuery) -> FormTemplateResult:
        template = await self._template_repo.get_by_id(request.template_id)
        return to_template_result(template)
