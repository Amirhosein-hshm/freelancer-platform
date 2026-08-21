from datetime import datetime
from decimal import Decimal

from app.application.project.dto import (
    CreateProjectCommand,
    CreateProjectResult,
    FormValueInput,
)
from app.application.project.form_validation import validate_form_values
from app.application.project.permissions import PERMISSION_PROJECT_CREATE_OWN
from app.application.project.status_history import record_status_history
from app.application.shared.authorization import IAuthorizationService
from app.application.shared.ports import (
    IClock,
    IIdGenerator,
    IProjectCodeGenerator,
    IUnitOfWork,
)
from app.application.shared.use_case import UseCase
from app.domain.form.enums import FormTemplateStatus
from app.domain.form.exceptions import FormTemplateNotPublishedError
from app.domain.form.repositories import IFormTemplateRepository
from app.domain.freelancer.enums import FreelancerLevelEnum
from app.domain.project.entities import Project
from app.domain.project.enums import (
    BudgetType,
    ProjectPriority,
    ProjectStatus,
    ProjectVisibility,
)
from app.domain.project.repositories import (
    IProjectRepository,
    IProjectStatusHistoryRepository,
)
from app.domain.project.value_objects import Budget, ProjectCode
from app.domain.shared.types import EntityId


async def _create_project(
    *,
    customer_user_id: EntityId,
    created_by_user_id: EntityId,
    form_template_id: EntityId,
    title: str,
    description: str,
    visibility: ProjectVisibility,
    budget_type: BudgetType,
    currency_code: str,
    required_level: FreelancerLevelEnum | None,
    fixed_budget: Decimal | None,
    budget_min: Decimal | None,
    budget_max: Decimal | None,
    priority: ProjectPriority,
    application_deadline: datetime | None,
    form_values: list[FormValueInput],
    project_repo: IProjectRepository,
    form_template_repo: IFormTemplateRepository,
    status_history_repo: IProjectStatusHistoryRepository,
    project_code_generator: IProjectCodeGenerator,
    id_generator: IIdGenerator,
    clock: IClock,
    uow: IUnitOfWork,
) -> CreateProjectResult:
    # The client picks the template (see ListFormTemplates); the category is DERIVED from it
    # so the two can never disagree. Raises FormTemplateNotFoundError when absent/soft-deleted.
    template = await form_template_repo.get_by_id(form_template_id)
    if template.status != FormTemplateStatus.PUBLISHED:
        raise FormTemplateNotPublishedError(
            f"Form template {template.id} is '{template.status.value}'; projects can only be "
            "created against a PUBLISHED template."
        )
    validate_form_values(template, form_values)
    now = await clock.now()
    code_value = await project_code_generator.next_code(now.year)
    budget = Budget(
        budget_type=budget_type,
        fixed_amount=fixed_budget,
        min_amount=budget_min,
        max_amount=budget_max,
        currency_code=currency_code,
    )
    project = Project(
        id=await id_generator.new_id(),
        project_code=ProjectCode(code_value),
        customer_user_id=customer_user_id,
        created_by_user_id=created_by_user_id,
        category_id=template.category_id,
        form_template_id=template.id,
        required_level=required_level,
        assigned_supervisor_user_id=None,
        selected_application_id=None,
        title=title,
        description=description,
        visibility=visibility,
        priority=priority,
        budget=budget,
        status=ProjectStatus.DRAFT,
        application_deadline=application_deadline,
        start_at=None,
        due_at=None,
        completed_at=None,
        cancelled_at=None,
        locked_at=None,
        deleted_at=None,
        created_at=now,
    )
    async with uow:
        await project_repo.add(project)
        await record_status_history(
            status_history_repo,
            id_generator,
            project.id,
            None,
            ProjectStatus.DRAFT,
            created_by_user_id,
            "Project created.",
            now,
        )
        await uow.commit()
    return CreateProjectResult(
        project_id=project.id,
        project_code=project.project_code.value,
        status=project.status,
    )


class CreateProjectUseCase(UseCase[CreateProjectCommand, CreateProjectResult]):
    def __init__(
        self,
        authorization_service: IAuthorizationService,
        project_repo: IProjectRepository,
        form_template_repo: IFormTemplateRepository,
        status_history_repo: IProjectStatusHistoryRepository,
        project_code_generator: IProjectCodeGenerator,
        id_generator: IIdGenerator,
        clock: IClock,
        uow: IUnitOfWork,
    ) -> None:
        self._authorization_service = authorization_service
        self._project_repo = project_repo
        self._form_template_repo = form_template_repo
        self._status_history_repo = status_history_repo
        self._project_code_generator = project_code_generator
        self._id_generator = id_generator
        self._clock = clock
        self._uow = uow

    async def execute(self, request: CreateProjectCommand) -> CreateProjectResult:
        await self._authorization_service.require_permission(request.actor_id, PERMISSION_PROJECT_CREATE_OWN)
        request.validate()
        return await _create_project(
            customer_user_id=request.actor_id,
            created_by_user_id=request.actor_id,
            form_template_id=request.form_template_id,
            title=request.title,
            description=request.description,
            visibility=request.visibility,
            budget_type=request.budget_type,
            currency_code=request.currency_code,
            required_level=request.required_level,
            fixed_budget=request.fixed_budget,
            budget_min=request.budget_min,
            budget_max=request.budget_max,
            priority=request.priority,
            application_deadline=request.application_deadline,
            form_values=request.form_values,
            project_repo=self._project_repo,
            form_template_repo=self._form_template_repo,
            status_history_repo=self._status_history_repo,
            project_code_generator=self._project_code_generator,
            id_generator=self._id_generator,
            clock=self._clock,
            uow=self._uow,
        )
