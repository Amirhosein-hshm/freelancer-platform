from app.application.project.dto import (
    CloseProjectRevisionRequestCommand,
    CloseProjectRevisionRequestResult,
)
from app.application.project.permissions import (
    PERMISSION_PROJECT_MANAGE_ANY,
    PERMISSION_PROJECT_MANAGE_OWN,
)
from app.application.shared.authorization import IAuthorizationService, authorize_owned_action
from app.application.shared.ports import IClock
from app.application.shared.use_case import UseCase
from app.domain.project.repositories import (
    IProjectRepository,
    IProjectRevisionRequestRepository,
)


class CloseProjectRevisionRequestUseCase(
    UseCase[CloseProjectRevisionRequestCommand, CloseProjectRevisionRequestResult]
):
    def __init__(
        self,
        authorization_service: IAuthorizationService,
        project_repo: IProjectRepository,
        revision_repo: IProjectRevisionRequestRepository,
        clock: IClock,
    ) -> None:
        self._authorization_service = authorization_service
        self._project_repo = project_repo
        self._revision_repo = revision_repo
        self._clock = clock

    async def execute(self, request: CloseProjectRevisionRequestCommand) -> CloseProjectRevisionRequestResult:
        revision = await self._revision_repo.get_by_id(request.revision_id)
        project = await self._project_repo.get_by_id(revision.project_id)
        await authorize_owned_action(
            self._authorization_service,
            request.actor_id,
            project.customer_user_id,
            PERMISSION_PROJECT_MANAGE_OWN,
            PERMISSION_PROJECT_MANAGE_ANY,
        )
        revision.close(request.actor_id, await self._clock.now())
        await self._revision_repo.update(revision)
        return CloseProjectRevisionRequestResult(revision_id=revision.id, status=revision.status.value)
