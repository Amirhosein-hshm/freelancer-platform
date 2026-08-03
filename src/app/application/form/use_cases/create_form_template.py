from app.application.form.dto import (
    CreateFormTemplateCommand,
    CreateFormTemplateResult,
)
from app.application.shared.authorization import IAuthorizationService
from app.application.shared.ports import IClock, IIdGenerator, IUnitOfWork
from app.application.shared.use_case import UseCase
from app.domain.form.entities import FormTemplate
from app.domain.form.enums import FormTemplateStatus
from app.domain.form.repositories import IFormTemplateRepository

PERMISSION_FORM_MANAGE = "form.manage"


class CreateFormTemplateUseCase(
    UseCase[CreateFormTemplateCommand, CreateFormTemplateResult]
):
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

    def execute(self, request: CreateFormTemplateCommand) -> CreateFormTemplateResult:
        self._authorization_service.require_permission(
            request.actor_id, PERMISSION_FORM_MANAGE
        )
        request.validate()
        now = self._clock.now()
        template = FormTemplate(
            id=self._id_generator.new_id(),
            category_id=request.category_id,
            template_key=request.template_key,
            name=request.name,
            version_no=1,
            status=FormTemplateStatus.DRAFT,
            is_active=True,
            published_by_user_id=None,
            published_at=None,
            fields=[],
            deleted_at=None,
            created_at=now,
        )
        with self._uow:
            self._template_repo.add(template)
            self._uow.commit()
        return CreateFormTemplateResult(
            template_id=template.id,
            version_no=template.version_no,
            status=template.status,
        )
