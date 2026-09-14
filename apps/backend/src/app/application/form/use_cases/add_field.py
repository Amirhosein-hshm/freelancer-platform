from app.application.form.dto import AddFieldCommand, AddFieldResult
from app.application.form.use_cases.create_form_template import PERMISSION_FORM_MANAGE
from app.application.shared.authorization import IAuthorizationService
from app.application.shared.ports import IClock, IIdGenerator, IUnitOfWork
from app.application.shared.use_case import UseCase
from app.domain.form.entities import FormField
from app.domain.form.repositories import IFormTemplateRepository


class AddFieldUseCase(UseCase[AddFieldCommand, AddFieldResult]):
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

    async def execute(self, request: AddFieldCommand) -> AddFieldResult:
        await self._authorization_service.require_permission(request.actor_id, PERMISSION_FORM_MANAGE)
        request.validate()
        template = await self._template_repo.get_by_id(request.template_id)
        now = await self._clock.now()
        field = FormField(
            id=await self._id_generator.new_id(),
            field_key=request.field_key,
            label=request.label,
            description=request.description,
            field_type=request.field_type,
            is_required=request.is_required,
            is_repeatable=request.is_repeatable,
            is_unique=request.is_unique,
            sort_order=request.sort_order,
            validation_rules=request.validation_rules,
            is_active=True,
            created_at=now,
        )
        async with self._uow:
            template.add_field(field)
            await self._template_repo.update(template)
            await self._uow.commit()
        return AddFieldResult(field_id=field.id)
