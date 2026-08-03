from app.application.form.dto import (
    PublishFormTemplateCommand,
    PublishFormTemplateResult,
)
from app.application.form.use_cases.create_form_template import PERMISSION_FORM_MANAGE
from app.application.shared.authorization import IAuthorizationService
from app.application.shared.ports import IClock, IUnitOfWork
from app.application.shared.use_case import UseCase
from app.domain.form.repositories import IFormTemplateRepository


class PublishFormTemplateUseCase(
    UseCase[PublishFormTemplateCommand, PublishFormTemplateResult]
):
    def __init__(
        self,
        authorization_service: IAuthorizationService,
        template_repo: IFormTemplateRepository,
        clock: IClock,
        uow: IUnitOfWork,
    ) -> None:
        self._authorization_service = authorization_service
        self._template_repo = template_repo
        self._clock = clock
        self._uow = uow

    def execute(self, request: PublishFormTemplateCommand) -> PublishFormTemplateResult:
        self._authorization_service.require_permission(
            request.published_by, PERMISSION_FORM_MANAGE
        )
        template = self._template_repo.get_by_id(request.template_id)
        now = self._clock.now()
        with self._uow:
            template.publish(request.published_by, now)
            self._template_repo.update(template)
            self._uow.commit()
        published_at = template.published_at
        assert published_at is not None
        return PublishFormTemplateResult(
            template_id=template.id,
            status=template.status,
            published_at=published_at,
        )
