from app.application.project.dto import (
    RequestRevisionCommand,
    RequestRevisionResult,
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
from app.domain.freelancer.repositories import IFreelancerProfileRepository
from app.domain.project.entities import ProjectRevisionRequest
from app.domain.project.enums import ProjectStatus, RevisionRequestStatus
from app.domain.project.repositories import (
    IProjectApplicationRepository,
    IProjectDeliveryRepository,
    IProjectRepository,
    IProjectRevisionRequestRepository,
    IProjectStatusHistoryRepository,
)
from app.domain.project.services import RevisionPolicy


class RequestRevisionUseCase(UseCase[RequestRevisionCommand, RequestRevisionResult]):
    def __init__(
        self,
        authorization_service: IAuthorizationService,
        project_repo: IProjectRepository,
        revision_repo: IProjectRevisionRequestRepository,
        delivery_repo: IProjectDeliveryRepository,
        status_history_repo: IProjectStatusHistoryRepository,
        id_generator: IIdGenerator,
        clock: IClock,
        uow: IUnitOfWork,
        application_repo: IProjectApplicationRepository,
        profile_repo: IFreelancerProfileRepository,
    ) -> None:
        self._authorization_service = authorization_service
        self._project_repo = project_repo
        self._revision_repo = revision_repo
        self._delivery_repo = delivery_repo
        self._status_history_repo = status_history_repo
        self._id_generator = id_generator
        self._clock = clock
        self._uow = uow
        self._application_repo = application_repo
        self._profile_repo = profile_repo

    async def execute(self, request: RequestRevisionCommand) -> RequestRevisionResult:
        project = await self._project_repo.get_by_id(request.project_id)
        await authorize_owned_action(
            self._authorization_service,
            request.actor_id,
            project.customer_user_id,
            PERMISSION_PROJECT_MANAGE_OWN,
            PERMISSION_PROJECT_MANAGE_ANY,
        )
        existing = await self._revision_repo.list_by_project(project.id)
        RevisionPolicy.ensure_can_request_new_revision(existing)
        from_status = project.status
        latest = await self._delivery_repo.get_latest_for_project(project.id)
        if project.selected_application_id is None:
            raise ValueError("A selected freelancer is required before requesting a revision.")
        application = await self._application_repo.get_by_id(project.selected_application_id)
        profile = await self._profile_repo.get_by_id(application.freelancer_profile_id)
        now = await self._clock.now()
        revision = ProjectRevisionRequest(
            id=await self._id_generator.new_id(),
            project_id=project.id,
            project_delivery_id=latest.id if latest is not None else None,
            requested_by_user_id=request.actor_id,
            requested_to_user_id=profile.user_id,
            round_no=len(existing) + 1,
            status=RevisionRequestStatus.OPEN,
            reason=request.reason,
            resolved_by_user_id=None,
            requested_at=now,
            resolved_at=None,
            created_at=now,
        )
        async with self._uow:
            await self._revision_repo.add(revision)
            if latest is not None:
                latest.mark_revised()
                await self._delivery_repo.update(latest)
            project.request_revision()
            await record_status_history(
                self._status_history_repo,
                self._id_generator,
                project.id,
                from_status,
                ProjectStatus.REVISION_REQUESTED,
                request.actor_id,
                request.reason,
                now,
            )
            await self._project_repo.update(project)
            await self._uow.commit()
        return RequestRevisionResult(
            revision_id=revision.id,
            round_no=revision.round_no,
            project_status=project.status,
        )
