from app.application.project.dto import (
    RejectFreelancerCommand,
    RejectFreelancerResult,
)
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
from app.domain.project.repositories import (
    IProjectApplicationRepository,
    IProjectRepository,
)


class RejectFreelancerUseCase(UseCase[RejectFreelancerCommand, RejectFreelancerResult]):
    def __init__(
        self,
        authorization_service: IAuthorizationService,
        project_repo: IProjectRepository,
        application_repo: IProjectApplicationRepository,
        clock: IClock,
        uow: IUnitOfWork,
    ) -> None:
        self._authorization_service = authorization_service
        self._project_repo = project_repo
        self._application_repo = application_repo
        self._clock = clock
        self._uow = uow

    def execute(self, request: RejectFreelancerCommand) -> RejectFreelancerResult:
        application = self._application_repo.get_by_id(request.application_id)
        project = self._project_repo.get_by_id(application.project_id)
        authorize_owned_action(
            self._authorization_service,
            request.actor_id,
            project.customer_user_id,
            PERMISSION_PROJECT_MANAGE_OWN,
            PERMISSION_PROJECT_MANAGE_ANY,
        )
        now = self._clock.now()
        with self._uow:
            application.reject(request.actor_id, now, request.note)
            self._application_repo.update(application)
            self._uow.commit()
        return RejectFreelancerResult(
            application_id=application.id,
            status=application.status,
        )
