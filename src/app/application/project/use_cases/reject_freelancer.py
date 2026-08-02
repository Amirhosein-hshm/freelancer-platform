from app.application.project.dto import (
    RejectFreelancerCommand,
    RejectFreelancerResult,
)
from app.application.shared.exceptions import PermissionDeniedError
from app.application.shared.ports import IClock, IUnitOfWork
from app.application.shared.use_case import UseCase
from app.domain.project.repositories import (
    IProjectApplicationRepository,
    IProjectRepository,
)


class RejectFreelancerUseCase(UseCase[RejectFreelancerCommand, RejectFreelancerResult]):
    def __init__(
        self,
        project_repo: IProjectRepository,
        application_repo: IProjectApplicationRepository,
        clock: IClock,
        uow: IUnitOfWork,
    ) -> None:
        self._project_repo = project_repo
        self._application_repo = application_repo
        self._clock = clock
        self._uow = uow

    def execute(self, request: RejectFreelancerCommand) -> RejectFreelancerResult:
        application = self._application_repo.get_by_id(request.application_id)
        project = self._project_repo.get_by_id(application.project_id)
        if project.customer_user_id != request.actor_id:
            raise PermissionDeniedError(
                f"User {request.actor_id} does not own project {project.id}."
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
