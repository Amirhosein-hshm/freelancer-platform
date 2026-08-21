from app.application.project.dto import DeleteProjectCommand, DeleteProjectResult
from app.application.project.permissions import (
    PERMISSION_PROJECT_MANAGE_ANY,
    PERMISSION_PROJECT_MANAGE_OWN,
)
from app.application.shared.authorization import (
    IAuthorizationService,
    authorize_owned_action,
)
from app.application.shared.ports import IClock, IUnitOfWork
from app.application.shared.use_case import UseCase
from app.domain.project.repositories import IProjectRepository


class DeleteProjectUseCase(UseCase[DeleteProjectCommand, DeleteProjectResult]):
    """Soft-deletes a DRAFT project.

    Past DRAFT this raises ``ProjectNotDraftError`` (HTTP 409) whose message directs the
    caller to ``CancelProject`` — a published project has applicants and history, so it must
    be cancelled rather than made to disappear. Every project read path filters
    ``deleted_at IS NULL`` (§12.6), so a deleted draft stops surfacing immediately.
    """

    def __init__(
        self,
        authorization_service: IAuthorizationService,
        project_repo: IProjectRepository,
        clock: IClock,
        uow: IUnitOfWork,
    ) -> None:
        self._authorization_service = authorization_service
        self._project_repo = project_repo
        self._clock = clock
        self._uow = uow

    async def execute(self, request: DeleteProjectCommand) -> DeleteProjectResult:
        project = await self._project_repo.get_by_id(request.project_id)
        await authorize_owned_action(
            self._authorization_service,
            request.actor_id,
            project.customer_user_id,
            PERMISSION_PROJECT_MANAGE_OWN,
            PERMISSION_PROJECT_MANAGE_ANY,
        )
        now = await self._clock.now()
        async with self._uow:
            project.soft_delete(now)
            await self._project_repo.update(project)
            await self._uow.commit()
        return DeleteProjectResult(project_id=project.id, deleted_at=now)
