from app.application.project.status_history import record_status_history
from app.application.review.dto import ReviewDeliveryResult
from app.application.shared.authorization import IAuthorizationService
from app.application.shared.exceptions import ValidationError
from app.application.shared.ports import IClock, IIdGenerator, IUnitOfWork
from app.domain.category.repositories import ICategorySupervisorRepository
from app.domain.project.entities import ProjectRevisionRequest
from app.domain.project.enums import ProjectStatus, RevisionRequestStatus
from app.domain.project.repositories import (
    IProjectDeliveryRepository,
    IProjectRepository,
    IProjectRevisionRequestRepository,
    IProjectStatusHistoryRepository,
)
from app.domain.project.services import RevisionPolicy
from app.domain.review.entities import SupervisorReview
from app.domain.review.enums import ReviewStatus
from app.domain.review.exceptions import DeliveryAlreadyReviewedError
from app.domain.review.repositories import ISupervisorReviewRepository
from app.domain.shared.exceptions import InvalidStateTransitionError
from app.domain.shared.types import EntityId

PERMISSION_REVIEW_DECIDE_OWN = "review.decide_own"
PERMISSION_REVIEW_DECIDE_ANY = "review.decide_any"


async def decide_delivery_review(
    *,
    authorization_service: IAuthorizationService,
    delivery_repo: IProjectDeliveryRepository,
    project_repo: IProjectRepository,
    category_supervisor_repo: ICategorySupervisorRepository,
    review_repo: ISupervisorReviewRepository,
    revision_repo: IProjectRevisionRequestRepository,
    status_history_repo: IProjectStatusHistoryRepository,
    id_generator: IIdGenerator,
    clock: IClock,
    uow: IUnitOfWork,
    actor_id: EntityId,
    delivery_id: EntityId,
    decision: ReviewStatus,
    notes: str | None,
    reject_reason: str | None,
) -> ReviewDeliveryResult:
    delivery = await delivery_repo.get_by_id(delivery_id)
    project = await project_repo.get_by_id(delivery.project_id)
    if project.status != ProjectStatus.UNDER_SUPERVISOR_REVIEW:
        raise InvalidStateTransitionError(
            f"Project {project.id} is '{project.status.value}'; delivery review is only "
            "allowed while the project is under supervisor review."
        )
    if await category_supervisor_repo.is_supervisor_of(actor_id, project.category_id):
        await authorization_service.require_permission(actor_id, PERMISSION_REVIEW_DECIDE_OWN)
    else:
        await authorization_service.require_permission(actor_id, PERMISSION_REVIEW_DECIDE_ANY)
    existing = await review_repo.find_by_delivery(delivery.id)
    if existing is not None and existing.decision != ReviewStatus.PENDING:
        raise DeliveryAlreadyReviewedError(
            f"Delivery {delivery.id} has already been reviewed ({existing.decision.value})."
        )
    now = await clock.now()
    async with uow:
        if existing is not None:
            review = existing
        else:
            review = SupervisorReview(
                id=await id_generator.new_id(),
                project_delivery_id=delivery.id,
                project_id=project.id,
                supervisor_user_id=actor_id,
                decision=ReviewStatus.PENDING,
                reject_reason=None,
                notes=None,
                reviewed_at=None,
                created_at=now,
            )
        if decision == ReviewStatus.APPROVED:
            review.approve(notes, now)
            delivery.approve(actor_id, now)
            project.move_to_customer_review()
            target = ProjectStatus.AWAITING_CUSTOMER_REVIEW
            reason = f"Supervisor approved delivery {delivery.id}."
        elif decision == ReviewStatus.REJECTED:
            existing_revisions = await revision_repo.list_by_project(project.id)
            RevisionPolicy.ensure_can_request_new_revision(existing_revisions)
            review.reject(reject_reason or "No reason given", now)
            delivery.reject(actor_id, now)
            revision = ProjectRevisionRequest(
                id=await id_generator.new_id(),
                project_id=project.id,
                project_delivery_id=delivery.id,
                requested_by_user_id=actor_id,
                requested_to_user_id=None,
                round_no=len(existing_revisions) + 1,
                status=RevisionRequestStatus.OPEN,
                reason=reject_reason or "Delivery rejected by supervisor.",
                resolved_by_user_id=None,
                requested_at=now,
                resolved_at=None,
                created_at=now,
            )
            await revision_repo.add(revision)
            project.request_revision()
            target = ProjectStatus.REVISION_REQUESTED
            reason = f"Supervisor rejected delivery {delivery.id}."
        else:
            raise ValidationError(f"Decision '{decision.value}' is not a valid review decision.")
        await record_status_history(
            status_history_repo,
            id_generator,
            project.id,
            ProjectStatus.UNDER_SUPERVISOR_REVIEW,
            target,
            actor_id,
            reason,
            now,
        )
        if existing is not None:
            await review_repo.update(review)
        else:
            await review_repo.add(review)
        await delivery_repo.update(delivery)
        await project_repo.update(project)
        await uow.commit()
    return ReviewDeliveryResult(
        delivery_id=delivery.id,
        project_id=project.id,
        decision=review.decision,
        project_status=project.status,
    )
