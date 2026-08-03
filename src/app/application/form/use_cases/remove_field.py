from app.application.form.dto import (
    RemoveFieldCommand,
    RemoveFieldResult,
)
from app.application.form.use_cases.create_form_template import PERMISSION_FORM_MANAGE
from app.application.shared.authorization import IAuthorizationService
from app.application.shared.ports import IUnitOfWork
from app.application.shared.use_case import UseCase
from app.domain.form.repositories import IFormTemplateRepository


class RemoveFieldUseCase(UseCase[RemoveFieldCommand, RemoveFieldResult]):
    def __init__(
        self,
        authorization_service: IAuthorizationService,
        template_repo: IFormTemplateRepository,
        uow: IUnitOfWork,
    ) -> None:
        self._authorization_service = authorization_service
        self._template_repo = template_repo
        self._uow = uow

    def execute(self, request: RemoveFieldCommand) -> RemoveFieldResult:
        self._authorization_service.require_permission(
            request.actor_id, PERMISSION_FORM_MANAGE
        )
        template = self._template_repo.get_by_id(request.template_id)
        with self._uow:
            template.remove_field(request.field_id)
            self._template_repo.update(template)
            self._uow.commit()
        return RemoveFieldResult(field_id=request.field_id)
