from app.application.project.dto import (
    SubmitDeliveryCommand,
    SubmitDeliveryResult,
)
from app.application.project.status_history import record_status_history
from app.application.shared.exceptions import PermissionDeniedError
from app.application.shared.ports import IClock, IIdGenerator, IUnitOfWork
from app.application.shared.use_case import UseCase
from app.domain.freelancer.repositories import IFreelancerProfileRepository
from app.domain.project.entities import ProjectDelivery
from app.domain.project.enums import DeliveryStatus, ProjectStatus
from app.domain.project.repositories import (
    IProjectApplicationRepository,
    IProjectDeliveryRepository,
    IProjectRepository,
    IProjectStatusHistoryRepository,
)


class SubmitDeliveryUseCase(UseCase[SubmitDeliveryCommand, SubmitDeliveryResult]):
    def __init__(
        self,
        project_repo: IProjectRepository,
        application_repo: IProjectApplicationRepository,
        delivery_repo: IProjectDeliveryRepository,
        status_history_repo: IProjectStatusHistoryRepository,
        profile_repo: IFreelancerProfileRepository,
        id_generator: IIdGenerator,
        clock: IClock,
        uow: IUnitOfWork,
    ) -> None:
        self._project_repo = project_repo
        self._application_repo = application_repo
        self._delivery_repo = delivery_repo
        self._status_history_repo = status_history_repo
        self._profile_repo = profile_repo
        self._id_generator = id_generator
        self._clock = clock
        self._uow = uow

    def execute(self, request: SubmitDeliveryCommand) -> SubmitDeliveryResult:
        project = self._project_repo.get_by_id(request.project_id)
        if project.selected_application_id is None:
            raise PermissionDeniedError(
                f"Project {project.id} has no selected freelancer."
            )
        selected = self._application_repo.get_by_id(project.selected_application_id)
        profile = self._profile_repo.get_by_id(selected.freelancer_profile_id)
        if profile.user_id != request.actor_id:
            raise PermissionDeniedError(
                f"User {request.actor_id} is not the selected freelancer of project "
                f"{project.id}."
            )
        previous = self._delivery_repo.get_latest_for_project(project.id)
        was_revision_requested = project.status == ProjectStatus.REVISION_REQUESTED
        version_no = (previous.version_no + 1) if previous is not None else 1
        now = self._clock.now()
        delivery = ProjectDelivery(
            id=self._id_generator.new_id(),
            project_id=project.id,
            version_no=version_no,
            submitted_by_user_id=request.actor_id,
            status=DeliveryStatus.SUBMITTED,
            delivery_note=request.delivery_note,
            submitted_at=now,
            reviewed_at=None,
            reviewer_user_id=None,
            superseded_by_delivery_id=None,
            file_asset_ids=list(request.file_asset_ids),
            created_at=now,
        )
        with self._uow:
            self._delivery_repo.add(delivery)
            if previous is not None and was_revision_requested:
                previous.supersede(delivery.id)
                self._delivery_repo.update(previous)
            project.mark_delivery_submitted()
            record_status_history(
                self._status_history_repo,
                self._id_generator,
                project.id,
                ProjectStatus.IN_PROGRESS
                if not was_revision_requested
                else ProjectStatus.REVISION_REQUESTED,
                ProjectStatus.DELIVERY_SUBMITTED,
                request.actor_id,
                None,
                now,
            )
            if project.has_supervisor():
                project.move_to_supervisor_review()
                delivery.mark_under_review()
                self._delivery_repo.update(delivery)
                target = ProjectStatus.UNDER_SUPERVISOR_REVIEW
            else:
                project.move_to_customer_review()
                target = ProjectStatus.AWAITING_CUSTOMER_REVIEW
            record_status_history(
                self._status_history_repo,
                self._id_generator,
                project.id,
                ProjectStatus.DELIVERY_SUBMITTED,
                target,
                request.actor_id,
                None,
                now,
            )
            self._project_repo.update(project)
            self._uow.commit()
        return SubmitDeliveryResult(
            delivery_id=delivery.id,
            version_no=delivery.version_no,
            project_status=project.status,
        )
