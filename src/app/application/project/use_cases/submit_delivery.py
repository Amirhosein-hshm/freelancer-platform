from app.application.project.dto import (
    SubmitDeliveryCommand,
    SubmitDeliveryResult,
)
from app.application.project.status_history import record_status_history
from app.application.shared.exceptions import PermissionDeniedError, ValidationError
from app.application.shared.ports import IClock, IFileStorageService, IIdGenerator, IUnitOfWork, IRealtimeNotifier, publish_project_event
from app.application.shared.use_case import UseCase
from app.domain.freelancer.repositories import IFreelancerProfileRepository
from app.domain.project.entities import ProjectDelivery
from app.domain.project.enums import DeliveryStatus, ProjectStatus
from app.domain.project.repositories import (
    IProjectApplicationRepository,
    IProjectDeliveryRepository,
    IProjectRepository,
    IProjectRevisionRequestRepository,
    IProjectStatusHistoryRepository,
)
from app.domain.review.entities import SupervisorReview
from app.domain.review.enums import ReviewStatus
from app.domain.review.repositories import ISupervisorReviewRepository


class SubmitDeliveryUseCase(UseCase[SubmitDeliveryCommand, SubmitDeliveryResult]):
    def __init__(
        self,
        project_repo: IProjectRepository,
        application_repo: IProjectApplicationRepository,
        delivery_repo: IProjectDeliveryRepository,
        status_history_repo: IProjectStatusHistoryRepository,
        profile_repo: IFreelancerProfileRepository,
        review_repo: ISupervisorReviewRepository,
        revision_repo: IProjectRevisionRequestRepository,
        file_storage: IFileStorageService,
        id_generator: IIdGenerator,
        clock: IClock,
        uow: IUnitOfWork,
        notifier: IRealtimeNotifier | None = None,
    ) -> None:
        self._project_repo = project_repo
        self._application_repo = application_repo
        self._delivery_repo = delivery_repo
        self._status_history_repo = status_history_repo
        self._profile_repo = profile_repo
        self._review_repo = review_repo
        self._revision_repo = revision_repo
        self._file_storage = file_storage
        self._id_generator = id_generator
        self._clock = clock
        self._uow = uow
        self._notifier = notifier

    async def execute(self, request: SubmitDeliveryCommand) -> SubmitDeliveryResult:
        for file_asset_id in request.file_asset_ids:
            try:
                await self._file_storage.get_metadata(file_asset_id)
            except (KeyError, FileNotFoundError) as exc:
                raise ValidationError(f"File asset {file_asset_id} does not exist.") from exc
        project = await self._project_repo.get_by_id(request.project_id)
        if project.selected_application_id is None:
            raise PermissionDeniedError(f"Project {project.id} has no selected freelancer.")
        selected = await self._application_repo.get_by_id(project.selected_application_id)
        profile = await self._profile_repo.get_by_id(selected.freelancer_profile_id)
        if profile.user_id != request.actor_id:
            raise PermissionDeniedError(
                f"User {request.actor_id} is not the selected freelancer of project {project.id}."
            )
        previous = await self._delivery_repo.get_latest_for_project(project.id)
        was_revision_requested = project.status == ProjectStatus.REVISION_REQUESTED
        version_no = (previous.version_no + 1) if previous is not None else 1
        now = await self._clock.now()
        delivery = ProjectDelivery(
            id=await self._id_generator.new_id(),
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
        async with self._uow:
            await self._delivery_repo.add(delivery)
            if previous is not None and was_revision_requested:
                previous.supersede(delivery.id)
                await self._delivery_repo.update(previous)
            if was_revision_requested:
                project.mark_revision_delivery_submitted()
                revisions = await self._revision_repo.list_by_project(project.id)
                open_revisions = [r for r in revisions if r.status.value == "open"]
                if open_revisions:
                    open_revisions[-1].close(request.actor_id, now)
                    await self._revision_repo.update(open_revisions[-1])
            else:
                project.mark_delivery_submitted()
            await record_status_history(
                self._status_history_repo,
                self._id_generator,
                project.id,
                ProjectStatus.IN_PROGRESS if not was_revision_requested else ProjectStatus.REVISION_REQUESTED,
                ProjectStatus.DELIVERY_SUBMITTED,
                request.actor_id,
                None,
                now,
            )
            if project.has_supervisor():
                project.move_to_supervisor_review()
                delivery.mark_under_review()
                await self._delivery_repo.update(delivery)
                assert project.assigned_supervisor_user_id is not None
                await self._review_repo.add(
                    SupervisorReview(
                        id=await self._id_generator.new_id(),
                        project_delivery_id=delivery.id,
                        project_id=project.id,
                        supervisor_user_id=project.assigned_supervisor_user_id,
                        decision=ReviewStatus.PENDING,
                        reject_reason=None,
                        notes=None,
                        reviewed_at=None,
                        created_at=now,
                    )
                )
                target = ProjectStatus.UNDER_SUPERVISOR_REVIEW
            else:
                project.move_to_customer_review()
                target = ProjectStatus.AWAITING_CUSTOMER_REVIEW
            await record_status_history(
                self._status_history_repo,
                self._id_generator,
                project.id,
                ProjectStatus.DELIVERY_SUBMITTED,
                target,
                request.actor_id,
                None,
                now,
            )
            await self._project_repo.update(project)
            await self._uow.commit()
        if self._notifier is not None:
            recipients = [project.customer_user_id]
            if project.assigned_supervisor_user_id is not None:
                recipients.append(project.assigned_supervisor_user_id)
            await publish_project_event(
                self._notifier,
                recipients,
                "project.delivery_submitted",
                {"project_id": project.id, "delivery_id": delivery.id, "status": project.status.value},
            )
        return SubmitDeliveryResult(
            delivery_id=delivery.id,
            version_no=delivery.version_no,
            project_status=project.status,
        )
