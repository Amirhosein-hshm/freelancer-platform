from app.application.form.dto import (
    PublishFormTemplateCommand,
    PublishFormTemplateResult,
)
from app.application.shared.ports import IClock, IUnitOfWork
from app.application.shared.use_case import UseCase
from app.domain.form.repositories import IFormTemplateRepository


class PublishFormTemplateUseCase(
    UseCase[PublishFormTemplateCommand, PublishFormTemplateResult]
):
    def __init__(
        self,
        template_repo: IFormTemplateRepository,
        clock: IClock,
        uow: IUnitOfWork,
    ) -> None:
        self._template_repo = template_repo
        self._clock = clock
        self._uow = uow

    def execute(self, request: PublishFormTemplateCommand) -> PublishFormTemplateResult:
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
