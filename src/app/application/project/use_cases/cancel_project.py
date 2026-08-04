from app.application.project.dto import (
    CancelProjectCommand,
    CancelProjectResult,
)
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


class CancelProjectUseCase(UseCase[CancelProjectCommand, CancelProjectResult]):
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

    async def execute(self, request: CancelProjectCommand) -> CancelProjectResult:
        project = await self._project_repo.get_by_id(request.project_id)
        await authorize_owned_action(
            self._authorization_service,
            request.actor_id,
            project.customer_user_id,
            PERMISSION_PROJECT_MANAGE_OWN,
            PERMISSION_PROJECT_MANAGE_ANY,
        )
        now = await self._clock.now()
        from_status = project.status
        async with self._uow:
            project.cancel(now, request.reason)
            await record_status_history(
                self._status_history_repo,
                self._id_generator,
                project.id,
                from_status,
                ProjectStatus.CANCELLED,
                request.actor_id,
                request.reason,
                now,
            )
            await self._project_repo.update(project)
            await self._uow.commit()
        return CancelProjectResult(project_id=project.id, status=project.status)
