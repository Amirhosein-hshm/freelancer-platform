from app.application.form.dto import (
    UpdateFormTemplateCommand,
    UpdateFormTemplateResult,
)
from app.application.form.use_cases.create_form_template import PERMISSION_FORM_MANAGE
from app.application.shared.authorization import IAuthorizationService
from app.application.shared.use_case import UseCase
from app.domain.form.repositories import IFormTemplateRepository


class UpdateFormTemplateUseCase(
    UseCase[UpdateFormTemplateCommand, UpdateFormTemplateResult]
):
    def __init__(
        self,
        authorization_service: IAuthorizationService,
        template_repo: IFormTemplateRepository,
    ) -> None:
        self._authorization_service = authorization_service
        self._template_repo = template_repo

    def execute(self, request: UpdateFormTemplateCommand) -> UpdateFormTemplateResult:
        self._authorization_service.require_permission(
            request.actor_id, PERMISSION_FORM_MANAGE
        )
        request.validate()
        template = self._template_repo.get_by_id(request.template_id)
        template.require_draft("update its name")
        template.name = request.name
        self._template_repo.update(template)
        return UpdateFormTemplateResult(template_id=template.id, name=template.name)
