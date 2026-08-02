from app.application.form.dto import (
    AddFieldOptionCommand,
    AddFieldOptionResult,
)
from app.application.shared.ports import IClock, IIdGenerator, IUnitOfWork
from app.application.shared.use_case import UseCase
from app.domain.form.entities import FormFieldOption
from app.domain.form.repositories import IFormTemplateRepository


class AddFieldOptionUseCase(UseCase[AddFieldOptionCommand, AddFieldOptionResult]):
    def __init__(
        self,
        template_repo: IFormTemplateRepository,
        id_generator: IIdGenerator,
        clock: IClock,
        uow: IUnitOfWork,
    ) -> None:
        self._template_repo = template_repo
        self._id_generator = id_generator
        self._clock = clock
        self._uow = uow

    def execute(self, request: AddFieldOptionCommand) -> AddFieldOptionResult:
        request.validate()
        template = self._template_repo.get_by_id(request.template_id)
        template.require_draft("add options")
        field = template.get_field(request.field_id)
        now = self._clock.now()
        option = FormFieldOption(
            id=self._id_generator.new_id(),
            option_key=request.option_key,
            label=request.label,
            value=request.value,
            sort_order=request.sort_order,
            is_active=request.is_active,
            created_at=now,
        )
        with self._uow:
            field.add_option(option)
            self._template_repo.update(template)
            self._uow.commit()
        return AddFieldOptionResult(option_id=option.id)
