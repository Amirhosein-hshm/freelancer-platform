from app.application.form.dto import (
    UpdateFieldCommand,
    UpdateFieldResult,
)
from app.application.form.use_cases.create_form_template import PERMISSION_FORM_MANAGE
from app.application.shared.authorization import IAuthorizationService
from app.application.shared.use_case import UseCase
from app.domain.form.repositories import IFormTemplateRepository


class UpdateFieldUseCase(UseCase[UpdateFieldCommand, UpdateFieldResult]):
    def __init__(
        self,
        authorization_service: IAuthorizationService,
        template_repo: IFormTemplateRepository,
    ) -> None:
        self._authorization_service = authorization_service
        self._template_repo = template_repo

    async def execute(self, request: UpdateFieldCommand) -> UpdateFieldResult:
        await self._authorization_service.require_permission(request.actor_id, PERMISSION_FORM_MANAGE)
        request.validate()
        template = await self._template_repo.get_by_id(request.template_id)
        template.require_draft("update fields")
        field = template.get_field(request.field_id)
        if request.label is not None:
            field.label = request.label
        if request.description is not None:
            field.description = request.description
        if request.field_type is not None:
            field.change_type(request.field_type)
        if request.is_required is not None:
            field.is_required = request.is_required
        if request.is_repeatable is not None:
            field.is_repeatable = request.is_repeatable
        if request.is_unique is not None:
            field.is_unique = request.is_unique
        if request.sort_order is not None:
            field.sort_order = request.sort_order
        if request.validation_rules is not None:
            field.validation_rules = request.validation_rules
        if request.is_active is not None:
            field.is_active = request.is_active
        await self._template_repo.update(template)
        return UpdateFieldResult(field_id=field.id)
