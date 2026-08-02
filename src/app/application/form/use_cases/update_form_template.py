from app.application.form.dto import (
    UpdateFormTemplateCommand,
    UpdateFormTemplateResult,
)
from app.application.shared.use_case import UseCase
from app.domain.form.repositories import IFormTemplateRepository


class UpdateFormTemplateUseCase(
    UseCase[UpdateFormTemplateCommand, UpdateFormTemplateResult]
):
    def __init__(self, template_repo: IFormTemplateRepository) -> None:
        self._template_repo = template_repo

    def execute(self, request: UpdateFormTemplateCommand) -> UpdateFormTemplateResult:
        request.validate()
        template = self._template_repo.get_by_id(request.template_id)
        template.require_draft("update its name")
        template.name = request.name
        self._template_repo.update(template)
        return UpdateFormTemplateResult(template_id=template.id, name=template.name)
