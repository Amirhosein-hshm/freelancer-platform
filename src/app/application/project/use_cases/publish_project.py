from app.application.project.dto import (
    PublishProjectCommand,
    PublishProjectResult,
)
from app.application.project.status_history import record_status_history
from app.application.shared.exceptions import PermissionDeniedError
from app.application.shared.ports import IClock, IIdGenerator, IUnitOfWork
from app.application.shared.use_case import UseCase
from app.domain.project.enums import ProjectStatus
from app.domain.project.repositories import (
    IProjectRepository,
    IProjectStatusHistoryRepository,
)


class PublishProjectUseCase(UseCase[PublishProjectCommand, PublishProjectResult]):
    def __init__(
        self,
        project_repo: IProjectRepository,
        status_history_repo: IProjectStatusHistoryRepository,
        id_generator: IIdGenerator,
        clock: IClock,
        uow: IUnitOfWork,
    ) -> None:
        self._project_repo = project_repo
        self._status_history_repo = status_history_repo
        self._id_generator = id_generator
        self._clock = clock
        self._uow = uow

    def execute(self, request: PublishProjectCommand) -> PublishProjectResult:
        project = self._project_repo.get_by_id(request.project_id)
        if project.customer_user_id != request.actor_id:
            raise PermissionDeniedError(
                f"User {request.actor_id} does not own project {request.project_id}."
            )
        now = self._clock.now()
        with self._uow:
            project.publish(now)
            record_status_history(
                self._status_history_repo,
                self._id_generator,
                project.id,
                ProjectStatus.DRAFT,
                ProjectStatus.PUBLISHED,
                request.actor_id,
                None,
                now,
            )
            project.start_collecting_applications()
            record_status_history(
                self._status_history_repo,
                self._id_generator,
                project.id,
                ProjectStatus.PUBLISHED,
                ProjectStatus.COLLECTING_APPLICATIONS,
                request.actor_id,
                None,
                now,
            )
            self._project_repo.update(project)
            self._uow.commit()
        return PublishProjectResult(project_id=project.id, status=project.status)
