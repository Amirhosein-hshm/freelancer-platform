from app.application.form.dto import (
    RemoveFieldOptionCommand,
    RemoveFieldOptionResult,
)
from app.application.form.use_cases.create_form_template import PERMISSION_FORM_MANAGE
from app.application.shared.authorization import IAuthorizationService
from app.application.shared.ports import IUnitOfWork
from app.application.shared.use_case import UseCase
from app.domain.form.repositories import IFormTemplateRepository


class RemoveFieldOptionUseCase(UseCase[RemoveFieldOptionCommand, RemoveFieldOptionResult]):
    def __init__(
        self,
        authorization_service: IAuthorizationService,
        template_repo: IFormTemplateRepository,
        uow: IUnitOfWork,
    ) -> None:
        self._authorization_service = authorization_service
        self._template_repo = template_repo
        self._uow = uow

    async def execute(self, request: RemoveFieldOptionCommand) -> RemoveFieldOptionResult:
        await self._authorization_service.require_permission(request.actor_id, PERMISSION_FORM_MANAGE)
        template = await self._template_repo.get_by_id(request.template_id)
        template.require_draft("remove field options")
        field = template.get_field(request.field_id)
        field.remove_option(request.option_id)
        async with self._uow:
            await self._template_repo.update(template)
            await self._uow.commit()
        return RemoveFieldOptionResult(option_id=request.option_id)
