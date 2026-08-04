from app.application.feedback.dto import SubmitReviewCommand, SubmitReviewResult
from app.application.feedback.permissions import (
    PERMISSION_FEEDBACK_MANAGE_ANY,
    PERMISSION_FEEDBACK_MANAGE_OWN,
)
from app.application.project.status_history import record_status_history
from app.application.shared.authorization import (
    IAuthorizationService,
    authorize_owned_action,
)
from app.application.shared.exceptions import ValidationError
from app.application.shared.ports import IClock, IIdGenerator, IUnitOfWork
from app.application.shared.use_case import UseCase
from app.domain.feedback.entities import CustomerReview
from app.domain.feedback.exceptions import ProjectNotCompletedError
from app.domain.feedback.repositories import ICustomerReviewRepository
from app.domain.project.entities import ProjectRevisionRequest
from app.domain.project.enums import ProjectStatus, RevisionRequestStatus
from app.domain.project.repositories import (
    IProjectDeliveryRepository,
    IProjectRepository,
    IProjectRevisionRequestRepository,
    IProjectStatusHistoryRepository,
)
from app.domain.project.services import RevisionPolicy
from app.domain.review.enums import ReviewStatus


class SubmitReviewUseCase(UseCase[SubmitReviewCommand, SubmitReviewResult]):
    def __init__(
        self,
        authorization_service: IAuthorizationService,
        project_repo: IProjectRepository,
        customer_review_repo: ICustomerReviewRepository,
        delivery_repo: IProjectDeliveryRepository,
        revision_repo: IProjectRevisionRequestRepository,
        status_history_repo: IProjectStatusHistoryRepository,
        id_generator: IIdGenerator,
        clock: IClock,
        uow: IUnitOfWork,
    ) -> None:
        self._authorization_service = authorization_service
        self._project_repo = project_repo
        self._customer_review_repo = customer_review_repo
        self._delivery_repo = delivery_repo
        self._revision_repo = revision_repo
        self._status_history_repo = status_history_repo
        self._id_generator = id_generator
        self._clock = clock
        self._uow = uow

    async def execute(self, request: SubmitReviewCommand) -> SubmitReviewResult:
        project = await self._project_repo.get_by_id(request.project_id)
        await authorize_owned_action(
            self._authorization_service,
            request.actor_id,
            project.customer_user_id,
            PERMISSION_FEEDBACK_MANAGE_OWN,
            PERMISSION_FEEDBACK_MANAGE_ANY,
        )
        if project.status != ProjectStatus.AWAITING_CUSTOMER_REVIEW:
            raise ProjectNotCompletedError(
                f"Project {project.id} is '{project.status.value}'; it must be "
                "awaiting customer review to submit a review."
            )
        latest = await self._delivery_repo.get_latest_for_project(project.id)
        if latest is None:
            raise ValidationError(
                f"Project {project.id} has no delivery to review."
            )
        now = await self._clock.now()
        review = CustomerReview(
            id=await self._id_generator.new_id(),
            project_id=project.id,
            project_delivery_id=latest.id,
            customer_user_id=request.actor_id,
            decision=request.decision,
            comment=request.comment,
            reviewed_at=now,
            created_at=now,
        )
        async with self._uow:
            await self._customer_review_repo.add(review)
            if request.decision == ReviewStatus.APPROVED:
                project.complete(now)
                target = ProjectStatus.COMPLETED
                reason = f"Customer approved project {project.id}."
            elif request.decision == ReviewStatus.REJECTED:
                latest.mark_revised()
                await self._delivery_repo.update(latest)
                existing = await self._revision_repo.list_by_project(project.id)
                RevisionPolicy.ensure_can_request_new_revision(existing)
                revision = ProjectRevisionRequest(
                    id=await self._id_generator.new_id(),
                    project_id=project.id,
                    project_delivery_id=latest.id,
                    requested_by_user_id=request.actor_id,
                    requested_to_user_id=None,
                    round_no=len(existing) + 1,
                    status=RevisionRequestStatus.OPEN,
                    reason=request.comment or "Delivery rejected by customer.",
                    resolved_by_user_id=None,
                    requested_at=now,
                    resolved_at=None,
                    created_at=now,
                )
                await self._revision_repo.add(revision)
                project.request_revision()
                target = ProjectStatus.REVISION_REQUESTED
                reason = request.comment or f"Customer rejected project {project.id}."
            else:
                raise ValidationError(
                    f"Decision '{request.decision.value}' is not a valid review decision."
                )
            await record_status_history(
                self._status_history_repo,
                self._id_generator,
                project.id,
                ProjectStatus.AWAITING_CUSTOMER_REVIEW,
                target,
                request.actor_id,
                reason,
                now,
            )
            await self._project_repo.update(project)
            await self._uow.commit()
        return SubmitReviewResult(
            review_id=review.id,
            project_id=project.id,
            decision=review.decision,
            project_status=project.status,
        )
