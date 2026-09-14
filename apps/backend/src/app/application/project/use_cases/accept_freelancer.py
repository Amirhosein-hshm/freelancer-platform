from app.application.project.dto import (
    AcceptFreelancerCommand,
    AcceptFreelancerResult,
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
from app.domain.project.enums import ProjectApplicationStatus, ProjectStatus
from app.domain.project.repositories import (
    IProjectApplicationRepository,
    IProjectRepository,
    IProjectStatusHistoryRepository,
)


class AcceptFreelancerUseCase(UseCase[AcceptFreelancerCommand, AcceptFreelancerResult]):
    def __init__(
        self,
        authorization_service: IAuthorizationService,
        project_repo: IProjectRepository,
        application_repo: IProjectApplicationRepository,
        status_history_repo: IProjectStatusHistoryRepository,
        id_generator: IIdGenerator,
        clock: IClock,
        uow: IUnitOfWork,
    ) -> None:
        self._authorization_service = authorization_service
        self._project_repo = project_repo
        self._application_repo = application_repo
        self._status_history_repo = status_history_repo
        self._id_generator = id_generator
        self._clock = clock
        self._uow = uow

    async def execute(self, request: AcceptFreelancerCommand) -> AcceptFreelancerResult:
        application = await self._application_repo.get_by_id(request.application_id)
        project = await self._project_repo.get_by_id(application.project_id)
        await authorize_owned_action(
            self._authorization_service,
            request.actor_id,
            project.customer_user_id,
            PERMISSION_PROJECT_MANAGE_OWN,
            PERMISSION_PROJECT_MANAGE_ANY,
        )
        now = await self._clock.now()
        async with self._uow:
            application.accept(request.actor_id, now)
            await self._application_repo.update(application)
            project.assign_freelancer(application.id, now)
            await record_status_history(
                self._status_history_repo,
                self._id_generator,
                project.id,
                ProjectStatus.COLLECTING_APPLICATIONS,
                ProjectStatus.ASSIGNED,
                request.actor_id,
                f"Freelancer application {application.id} accepted.",
                now,
            )
            for other in await self._application_repo.list_by_project(project.id):
                if other.id != application.id and other.status in (
                    ProjectApplicationStatus.APPLIED,
                    ProjectApplicationStatus.SHORTLISTED,
                ):
                    other.reject(request.actor_id, now, "Another freelancer was selected.")
                    await self._application_repo.update(other)
            await self._project_repo.update(project)
            await self._uow.commit()
        return AcceptFreelancerResult(
            project_id=project.id,
            selected_application_id=project.selected_application_id or application.id,
            status=project.status,
        )
