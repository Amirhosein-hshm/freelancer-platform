from app.application.project.dto import (
    CreateProjectCommand,
    CreateProjectResult,
)
from app.application.project.form_validation import validate_form_values
from app.application.project.status_history import record_status_history
from app.application.shared.ports import (
    IClock,
    IIdGenerator,
    IProjectCodeGenerator,
    IUnitOfWork,
)
from app.application.shared.use_case import UseCase
from app.domain.category.repositories import ICategoryRepository
from app.domain.form.repositories import IFormTemplateRepository
from app.domain.project.entities import Project
from app.domain.project.enums import ProjectStatus
from app.domain.project.repositories import (
    IProjectRepository,
    IProjectStatusHistoryRepository,
)
from app.domain.project.value_objects import Budget, ProjectCode


class CreateProjectUseCase(UseCase[CreateProjectCommand, CreateProjectResult]):
    def __init__(
        self,
        project_repo: IProjectRepository,
        category_repo: ICategoryRepository,
        form_template_repo: IFormTemplateRepository,
        status_history_repo: IProjectStatusHistoryRepository,
        project_code_generator: IProjectCodeGenerator,
        id_generator: IIdGenerator,
        clock: IClock,
        uow: IUnitOfWork,
    ) -> None:
        self._project_repo = project_repo
        self._category_repo = category_repo
        self._form_template_repo = form_template_repo
        self._status_history_repo = status_history_repo
        self._project_code_generator = project_code_generator
        self._id_generator = id_generator
        self._clock = clock
        self._uow = uow

    def execute(self, request: CreateProjectCommand) -> CreateProjectResult:
        request.validate()
        category = self._category_repo.get_by_id(request.category_id)
        template = self._form_template_repo.get_published_for_category(category.id)
        validate_form_values(template, request.form_values)
        now = self._clock.now()
        code_value = self._project_code_generator.next_code(now.year)
        budget = Budget(
            budget_type=request.budget_type,
            fixed_amount=request.fixed_budget,
            min_amount=request.budget_min,
            max_amount=request.budget_max,
            currency_code=request.currency_code,
        )
        project = Project(
            id=self._id_generator.new_id(),
            project_code=ProjectCode(code_value),
            customer_user_id=request.customer_user_id,
            category_id=category.id,
            form_template_id=template.id,
            assigned_supervisor_user_id=None,
            selected_application_id=None,
            title=request.title,
            description=request.description,
            visibility=request.visibility,
            priority=request.priority,
            budget=budget,
            status=ProjectStatus.DRAFT,
            application_deadline=request.application_deadline,
            start_at=None,
            due_at=None,
            completed_at=None,
            cancelled_at=None,
            locked_at=None,
            deleted_at=None,
            created_at=now,
        )
        with self._uow:
            self._project_repo.add(project)
            record_status_history(
                self._status_history_repo,
                self._id_generator,
                project.id,
                None,
                ProjectStatus.DRAFT,
                request.customer_user_id,
                "Project created.",
                now,
            )
            self._uow.commit()
        return CreateProjectResult(
            project_id=project.id,
            project_code=project.project_code.value,
            status=project.status,
        )
