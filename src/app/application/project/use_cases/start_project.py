from app.application.project.dto import StartProjectCommand, StartProjectResult
from app.application.project.permissions import (
    PERMISSION_PROJECT_MANAGE_ANY,
    PERMISSION_PROJECT_MANAGE_OWN,
)
from app.application.project.status_history import record_status_history
from app.application.shared.authorization import (
    IAuthorizationService,
    authorize_owned_action,
)
from app.application.shared.ports import IClock, IIdGenerator, IUnitOfWork
from app.application.shared.use_case import UseCase
from app.domain.project.enums import ProjectStatus
from app.domain.project.repositories import (
    IProjectRepository,
    IProjectStatusHistoryRepository,
)


class StartProjectUseCase(UseCase[StartProjectCommand, StartProjectResult]):
    def __init__(
        self,
        authorization_service: IAuthorizationService,
        project_repo: IProjectRepository,
        status_history_repo: IProjectStatusHistoryRepository,
        id_generator: IIdGenerator,
        clock: IClock,
        uow: IUnitOfWork,
    ) -> None:
        self._authorization_service = authorization_service
        self._project_repo = project_repo
        self._status_history_repo = status_history_repo
        self._id_generator = id_generator
        self._clock = clock
        self._uow = uow

    def execute(self, request: StartProjectCommand) -> StartProjectResult:
        project = self._project_repo.get_by_id(request.project_id)
        authorize_owned_action(
            self._authorization_service,
            request.actor_id,
            project.customer_user_id,
            PERMISSION_PROJECT_MANAGE_OWN,
            PERMISSION_PROJECT_MANAGE_ANY,
        )
        now = self._clock.now()
        with self._uow:
            project.start(now)
            record_status_history(
                self._status_history_repo,
                self._id_generator,
                project.id,
                ProjectStatus.ASSIGNED,
                ProjectStatus.IN_PROGRESS,
                request.actor_id,
                None,
                now,
            )
            self._project_repo.update(project)
            self._uow.commit()
        return StartProjectResult(project_id=project.id, status=project.status)
