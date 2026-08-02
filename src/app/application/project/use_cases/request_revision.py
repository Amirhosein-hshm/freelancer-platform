from app.application.project.dto import (
    RequestRevisionCommand,
    RequestRevisionResult,
)
from app.application.project.status_history import record_status_history
from app.application.shared.exceptions import PermissionDeniedError
from app.application.shared.ports import IClock, IIdGenerator, IUnitOfWork
from app.application.shared.use_case import UseCase
from app.domain.project.entities import ProjectRevisionRequest
from app.domain.project.enums import ProjectStatus, RevisionRequestStatus
from app.domain.project.exceptions import MaxRevisionsExceededError
from app.domain.project.repositories import (
    IProjectDeliveryRepository,
    IProjectRepository,
    IProjectRevisionRequestRepository,
    IProjectStatusHistoryRepository,
)
from app.domain.project.services import RevisionPolicy


class RequestRevisionUseCase(UseCase[RequestRevisionCommand, RequestRevisionResult]):
    def __init__(
        self,
        project_repo: IProjectRepository,
        revision_repo: IProjectRevisionRequestRepository,
        delivery_repo: IProjectDeliveryRepository,
        status_history_repo: IProjectStatusHistoryRepository,
        id_generator: IIdGenerator,
        clock: IClock,
        uow: IUnitOfWork,
    ) -> None:
        self._project_repo = project_repo
        self._revision_repo = revision_repo
        self._delivery_repo = delivery_repo
        self._status_history_repo = status_history_repo
        self._id_generator = id_generator
        self._clock = clock
        self._uow = uow

    def execute(self, request: RequestRevisionCommand) -> RequestRevisionResult:
        project = self._project_repo.get_by_id(request.project_id)
        if project.customer_user_id != request.actor_id:
            raise PermissionDeniedError(
                f"User {request.actor_id} cannot request a revision on project "
                f"{request.project_id}."
            )
        existing = self._revision_repo.list_by_project(project.id)
        if not RevisionPolicy.can_request_new_revision(existing):
            raise MaxRevisionsExceededError(
                f"Project {project.id} has reached the maximum of "
                f"{RevisionPolicy.MAX_REVISIONS} revisions."
            )
        latest = self._delivery_repo.get_latest_for_project(project.id)
        now = self._clock.now()
        revision = ProjectRevisionRequest(
            id=self._id_generator.new_id(),
            project_id=project.id,
            project_delivery_id=latest.id if latest is not None else None,
            requested_by_user_id=request.actor_id,
            requested_to_user_id=None,
            round_no=len(existing) + 1,
            status=RevisionRequestStatus.OPEN,
            reason=request.reason,
            resolved_by_user_id=None,
            requested_at=now,
            resolved_at=None,
            created_at=now,
        )
        with self._uow:
            self._revision_repo.add(revision)
            if latest is not None:
                latest.mark_revised()
                self._delivery_repo.update(latest)
            project.request_revision()
            record_status_history(
                self._status_history_repo,
                self._id_generator,
                project.id,
                project.status,
                ProjectStatus.REVISION_REQUESTED,
                request.actor_id,
                request.reason,
                now,
            )
            self._project_repo.update(project)
            self._uow.commit()
        return RequestRevisionResult(
            revision_id=revision.id,
            round_no=revision.round_no,
            project_status=project.status,
        )
