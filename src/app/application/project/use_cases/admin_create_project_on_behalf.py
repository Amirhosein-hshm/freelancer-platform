from app.application.project.dto import (
    CreateProjectOnBehalfCommand,
    CreateProjectResult,
)
from app.application.project.permissions import PERMISSION_PROJECT_CREATE_ON_BEHALF
from app.application.project.use_cases.create_project import _create_project
from app.application.shared.authorization import IAuthorizationService
from app.application.shared.ports import (
    IClock,
    IIdGenerator,
    IProjectCodeGenerator,
    IUnitOfWork,
)
from app.application.shared.use_case import UseCase
from app.domain.category.repositories import ICategoryRepository
from app.domain.form.repositories import IFormTemplateRepository
from app.domain.iam.repositories import IUserRepository
from app.domain.project.repositories import (
    IProjectRepository,
    IProjectStatusHistoryRepository,
)


class AdminCreateProjectOnBehalfUseCase(
    UseCase[CreateProjectOnBehalfCommand, CreateProjectResult]
):
    def __init__(
        self,
        authorization_service: IAuthorizationService,
        user_repo: IUserRepository,
        project_repo: IProjectRepository,
        category_repo: ICategoryRepository,
        form_template_repo: IFormTemplateRepository,
        status_history_repo: IProjectStatusHistoryRepository,
        project_code_generator: IProjectCodeGenerator,
        id_generator: IIdGenerator,
        clock: IClock,
        uow: IUnitOfWork,
    ) -> None:
        self._authorization_service = authorization_service
        self._user_repo = user_repo
        self._project_repo = project_repo
        self._category_repo = category_repo
        self._form_template_repo = form_template_repo
        self._status_history_repo = status_history_repo
        self._project_code_generator = project_code_generator
        self._id_generator = id_generator
        self._clock = clock
        self._uow = uow

    def execute(self, request: CreateProjectOnBehalfCommand) -> CreateProjectResult:
        self._authorization_service.require_permission(
            request.actor_id, PERMISSION_PROJECT_CREATE_ON_BEHALF
        )
        self._user_repo.get_by_id(request.target_customer_user_id)
        request.validate()
        return _create_project(
            customer_user_id=request.target_customer_user_id,
            created_by_user_id=request.actor_id,
            category_id=request.category_id,
            title=request.title,
            description=request.description,
            visibility=request.visibility,
            budget_type=request.budget_type,
            currency_code=request.currency_code,
            fixed_budget=request.fixed_budget,
            budget_min=request.budget_min,
            budget_max=request.budget_max,
            priority=request.priority,
            application_deadline=request.application_deadline,
            form_values=request.form_values,
            project_repo=self._project_repo,
            category_repo=self._category_repo,
            form_template_repo=self._form_template_repo,
            status_history_repo=self._status_history_repo,
            project_code_generator=self._project_code_generator,
            id_generator=self._id_generator,
            clock=self._clock,
            uow=self._uow,
        )
