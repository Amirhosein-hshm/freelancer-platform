from app.application.form.dto import (
    UpdateFieldOptionCommand,
    UpdateFieldOptionResult,
)
from app.application.form.use_cases.create_form_template import PERMISSION_FORM_MANAGE
from app.application.shared.authorization import IAuthorizationService
from app.application.shared.ports import IUnitOfWork
from app.application.shared.use_case import UseCase
from app.domain.form.repositories import IFormTemplateRepository


class UpdateFieldOptionUseCase(
    UseCase[UpdateFieldOptionCommand, UpdateFieldOptionResult]
):
    def __init__(
        self,
        authorization_service: IAuthorizationService,
        template_repo: IFormTemplateRepository,
        uow: IUnitOfWork,
    ) -> None:
        self._authorization_service = authorization_service
        self._template_repo = template_repo
        self._uow = uow

    async def execute(
        self, request: UpdateFieldOptionCommand
    ) -> UpdateFieldOptionResult:
        await self._authorization_service.require_permission(
            request.actor_id, PERMISSION_FORM_MANAGE
        )
        request.validate()
        template = await self._template_repo.get_by_id(request.template_id)
        template.require_draft("update field options")
        field = template.get_field(request.field_id)
        field.update_option(
            request.option_id,
            label=request.label,
            value=request.value,
            sort_order=request.sort_order,
            is_active=request.is_active,
        )
        async with self._uow:
            await self._template_repo.update(template)
            await self._uow.commit()
        return UpdateFieldOptionResult(option_id=request.option_id)
