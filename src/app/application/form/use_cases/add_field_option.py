from app.application.form.dto import (
    AddFieldOptionCommand,
    AddFieldOptionResult,
)
from app.application.form.use_cases.create_form_template import PERMISSION_FORM_MANAGE
from app.application.shared.authorization import IAuthorizationService
from app.application.shared.ports import IClock, IIdGenerator, IUnitOfWork
from app.application.shared.use_case import UseCase
from app.domain.form.entities import FormFieldOption
from app.domain.form.repositories import IFormTemplateRepository


class AddFieldOptionUseCase(UseCase[AddFieldOptionCommand, AddFieldOptionResult]):
    def __init__(
        self,
        authorization_service: IAuthorizationService,
        template_repo: IFormTemplateRepository,
        id_generator: IIdGenerator,
        clock: IClock,
        uow: IUnitOfWork,
    ) -> None:
        self._authorization_service = authorization_service
        self._template_repo = template_repo
        self._id_generator = id_generator
        self._clock = clock
        self._uow = uow

    async def execute(self, request: AddFieldOptionCommand) -> AddFieldOptionResult:
        await self._authorization_service.require_permission(
            request.actor_id, PERMISSION_FORM_MANAGE
        )
        request.validate()
        template = await self._template_repo.get_by_id(request.template_id)
        template.require_draft("add options")
        field = template.get_field(request.field_id)
        now = await self._clock.now()
        option = FormFieldOption(
            id=await self._id_generator.new_id(),
            option_key=request.option_key,
            label=request.label,
            value=request.value,
            sort_order=request.sort_order,
            is_active=request.is_active,
            created_at=now,
        )
        async with self._uow:
            field.add_option(option)
            await self._template_repo.update(template)
            await self._uow.commit()
        return AddFieldOptionResult(option_id=option.id)
