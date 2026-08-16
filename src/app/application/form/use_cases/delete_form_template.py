from app.application.form.dto import (
    DeleteFormTemplateCommand,
    DeleteFormTemplateResult,
)
from app.application.form.use_cases.create_form_template import PERMISSION_FORM_MANAGE
from app.application.shared.authorization import IAuthorizationService
from app.application.shared.ports import IUnitOfWork
from app.application.shared.use_case import UseCase
from app.domain.form.enums import FormTemplateStatus
from app.domain.form.exceptions import FormTemplateHasActiveReferencesError
from app.domain.form.repositories import IFormTemplateRepository
from app.domain.project.repositories import IProjectRepository


class DeleteFormTemplateUseCase(
    UseCase[DeleteFormTemplateCommand, DeleteFormTemplateResult]
):
    def __init__(
        self,
        authorization_service: IAuthorizationService,
        template_repo: IFormTemplateRepository,
        project_repo: IProjectRepository,
        uow: IUnitOfWork,
    ) -> None:
        self._authorization_service = authorization_service
        self._template_repo = template_repo
        self._project_repo = project_repo
        self._uow = uow

    async def execute(self, request: DeleteFormTemplateCommand) -> DeleteFormTemplateResult:
        await self._authorization_service.require_permission(
            request.actor_id, PERMISSION_FORM_MANAGE
        )
        template = await self._template_repo.get_by_id(request.template_id)
        if template.status != FormTemplateStatus.DRAFT:
            raise FormTemplateHasActiveReferencesError(
                f"Form template {template.id} cannot be deleted because it is not a DRAFT."
            )
        active_projects = await self._project_repo.count_active_by_form_template(
            template.id
        )
        if active_projects:
            raise FormTemplateHasActiveReferencesError(
                f"Form template {template.id} cannot be deleted because it is referenced "
                f"by {active_projects} active project{'s' if active_projects != 1 else ''}."
            )
        async with self._uow:
            await self._template_repo.delete(template.id)
            await self._uow.commit()
        return DeleteFormTemplateResult(template_id=template.id)
