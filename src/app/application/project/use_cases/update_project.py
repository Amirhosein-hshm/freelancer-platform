from app.application.project.dto import UpdateProjectCommand, UpdateProjectResult
from app.application.project.form_validation import validate_form_values
from app.application.project.permissions import (
    PERMISSION_PROJECT_MANAGE_ANY,
    PERMISSION_PROJECT_MANAGE_OWN,
)
from app.application.shared.authorization import (
    IAuthorizationService,
    authorize_owned_action,
)
from app.application.shared.ports import IUnitOfWork
from app.application.shared.use_case import UseCase
from app.domain.form.enums import FormTemplateStatus
from app.domain.form.exceptions import FormTemplateNotPublishedError
from app.domain.form.repositories import IFormTemplateRepository
from app.domain.project.repositories import IProjectRepository
from app.domain.project.value_objects import Budget


class UpdateProjectUseCase(UseCase[UpdateProjectCommand, UpdateProjectResult]):
    """Edits a project's customer-supplied fields while it is still DRAFT.

    Past DRAFT, ``Project.require_draft`` raises ``ProjectNotDraftError`` (HTTP 409) and the
    caller is pointed at ``CancelProject``. ``form_values`` are re-validated against the
    chosen form template exactly as ``CreateProject`` does — note they are validated but not
    persisted, since no form-value store exists (see docs §12.3).
    """

    def __init__(
        self,
        authorization_service: IAuthorizationService,
        project_repo: IProjectRepository,
        form_template_repo: IFormTemplateRepository,
        uow: IUnitOfWork,
    ) -> None:
        self._authorization_service = authorization_service
        self._project_repo = project_repo
        self._form_template_repo = form_template_repo
        self._uow = uow

    async def execute(self, request: UpdateProjectCommand) -> UpdateProjectResult:
        project = await self._project_repo.get_by_id(request.project_id)
        await authorize_owned_action(
            self._authorization_service,
            request.actor_id,
            project.customer_user_id,
            PERMISSION_PROJECT_MANAGE_OWN,
            PERMISSION_PROJECT_MANAGE_ANY,
        )
        request.validate()
        project.require_draft("be edited")
        # The client may switch templates while the project is a draft; the category follows.
        template = await self._form_template_repo.get_by_id(request.form_template_id)
        if template.status != FormTemplateStatus.PUBLISHED:
            raise FormTemplateNotPublishedError(
                f"Form template {template.id} is '{template.status.value}'; projects can only "
                "reference a PUBLISHED template."
            )
        validate_form_values(template, request.form_values)
        budget = Budget(
            budget_type=request.budget_type,
            fixed_amount=request.fixed_budget,
            min_amount=request.budget_min,
            max_amount=request.budget_max,
            currency_code=request.currency_code,
        )
        async with self._uow:
            project.update_details(
                category_id=template.category_id,
                form_template_id=template.id,
                required_level=request.required_level,
                title=request.title,
                description=request.description,
                visibility=request.visibility,
                priority=request.priority,
                budget=budget,
                application_deadline=request.application_deadline,
            )
            await self._project_repo.update(project)
            await self._uow.commit()
        return UpdateProjectResult(project_id=project.id, status=project.status)
