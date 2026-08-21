from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from app.domain.freelancer.enums import FreelancerLevelEnum
from app.domain.project.enums import (
    DeliveryStatus,
    ProjectApplicationStatus,
    ProjectPriority,
    ProjectStatus,
    ProjectVisibility,
    RevisionRequestStatus,
)
from app.domain.project.exceptions import (
    ApplicationAlreadyDecidedError,
    InvalidProjectStatusTransitionError,
    ProjectAlreadyAssignedError,
    ProjectLockedError,
    ProjectNotDraftError,
)
from app.domain.project.value_objects import Budget, ProjectCode
from app.domain.shared.entity import AggregateRoot, Entity
from app.domain.shared.exceptions import InvalidStateTransitionError
from app.domain.shared.types import EntityId

_LOCKED_STATUSES = (ProjectStatus.COMPLETED, ProjectStatus.CANCELLED)
_APPLICATION_OPEN_STATUSES = (ProjectStatus.PUBLISHED, ProjectStatus.COLLECTING_APPLICATIONS)


@dataclass(eq=False)
class Project(AggregateRoot):
    """Project aggregate root.

    ``publish`` transitions DRAFT -> PUBLISHED and ``start_collecting_applications``
    transitions PUBLISHED -> COLLECTING_APPLICATIONS. The two enum values are kept
    separate for precise status history, but the PublishProject use case performs both
    transitions back-to-back so a newly published project immediately reaches
    COLLECTING_APPLICATIONS.
    """

    project_code: ProjectCode
    customer_user_id: EntityId
    category_id: EntityId
    form_template_id: EntityId
    required_level: FreelancerLevelEnum | None
    assigned_supervisor_user_id: EntityId | None
    selected_application_id: EntityId | None
    title: str
    description: str
    visibility: ProjectVisibility
    priority: ProjectPriority
    budget: Budget
    status: ProjectStatus
    application_deadline: datetime | None
    start_at: datetime | None
    due_at: datetime | None
    completed_at: datetime | None
    cancelled_at: datetime | None
    locked_at: datetime | None
    deleted_at: datetime | None
    created_by_user_id: EntityId | None = None

    def publish(self, at: datetime) -> None:
        self._ensure_unlocked()
        self._transition(ProjectStatus.DRAFT, ProjectStatus.PUBLISHED)

    def start_collecting_applications(self) -> None:
        self._ensure_unlocked()
        self._transition(ProjectStatus.PUBLISHED, ProjectStatus.COLLECTING_APPLICATIONS)

    def assign_freelancer(self, application_id: EntityId, at: datetime) -> None:
        self._ensure_unlocked()
        if self.selected_application_id is not None:
            raise ProjectAlreadyAssignedError(
                f"Project {self.id} already has a selected freelancer "
                f"({self.selected_application_id}); only one freelancer per project."
            )
        self._transition(ProjectStatus.COLLECTING_APPLICATIONS, ProjectStatus.ASSIGNED)
        self.selected_application_id = application_id

    def start(self, at: datetime) -> None:
        self._ensure_unlocked()
        self._transition(ProjectStatus.ASSIGNED, ProjectStatus.IN_PROGRESS)
        self.start_at = at

    def mark_delivery_submitted(self) -> None:
        self._ensure_unlocked()
        if self.status not in (ProjectStatus.IN_PROGRESS, ProjectStatus.REVISION_REQUESTED):
            raise InvalidProjectStatusTransitionError(
                f"Project {self.id} is '{self.status.value}'; a delivery can only be "
                "submitted from IN_PROGRESS or REVISION_REQUESTED."
            )
        self.status = ProjectStatus.DELIVERY_SUBMITTED

    def move_to_supervisor_review(self) -> None:
        self._ensure_unlocked()
        self._transition(ProjectStatus.DELIVERY_SUBMITTED, ProjectStatus.UNDER_SUPERVISOR_REVIEW)
        if self.assigned_supervisor_user_id is None:
            raise InvalidProjectStatusTransitionError(
                f"Project {self.id} has no assigned supervisor and cannot move to supervisor review."
            )

    def move_to_customer_review(self) -> None:
        self._ensure_unlocked()
        if self.status == ProjectStatus.DELIVERY_SUBMITTED:
            self.status = ProjectStatus.AWAITING_CUSTOMER_REVIEW
            return
        if self.status == ProjectStatus.UNDER_SUPERVISOR_REVIEW:
            self.status = ProjectStatus.AWAITING_CUSTOMER_REVIEW
            return
        raise InvalidProjectStatusTransitionError(
            f"Project {self.id} is '{self.status.value}'; cannot move to customer review."
        )

    def request_revision(self) -> None:
        self._ensure_unlocked()
        if self.status not in (
            ProjectStatus.UNDER_SUPERVISOR_REVIEW,
            ProjectStatus.AWAITING_CUSTOMER_REVIEW,
        ):
            raise InvalidProjectStatusTransitionError(
                f"Project {self.id} is '{self.status.value}'; a revision can only be "
                "requested from supervisor or customer review."
            )
        self.status = ProjectStatus.REVISION_REQUESTED

    def complete(self, at: datetime) -> None:
        self._ensure_unlocked()
        self._transition(ProjectStatus.AWAITING_CUSTOMER_REVIEW, ProjectStatus.COMPLETED)
        self.completed_at = at
        self.locked_at = at

    def cancel(self, at: datetime, reason: str) -> None:
        if self.is_locked():
            raise ProjectLockedError(f"Project {self.id} is locked and cannot be cancelled.")
        self.status = ProjectStatus.CANCELLED
        self.cancelled_at = at
        self.locked_at = at

    def is_locked(self) -> bool:
        return self.status in _LOCKED_STATUSES

    def require_draft(self, action: str) -> None:
        """Guard for DRAFT-only operations, mirroring ``FormTemplate.require_draft``.

        The message points a caller past DRAFT at ``CancelProject``, which is the supported
        way to withdraw an already-published project.
        """
        if self.status != ProjectStatus.DRAFT:
            raise ProjectNotDraftError(
                f"Project {self.id} is '{self.status.value}' and cannot {action}; only DRAFT "
                "projects can be edited or deleted. Cancel the project instead."
            )

    def soft_delete(self, at: datetime) -> None:
        """DRAFT-only soft delete. Past DRAFT the supported path is ``cancel``."""
        self.require_draft("be deleted")
        if self.deleted_at is not None:
            raise InvalidStateTransitionError(f"Project {self.id} is already deleted.")
        self.deleted_at = at

    def update_details(
        self,
        *,
        category_id: EntityId,
        form_template_id: EntityId,
        required_level: FreelancerLevelEnum | None,
        title: str,
        description: str,
        visibility: ProjectVisibility,
        priority: ProjectPriority,
        budget: Budget,
        application_deadline: datetime | None,
    ) -> None:
        """DRAFT-only edit of the customer-supplied fields.

        ``category_id`` must always be the category of ``form_template_id`` — the caller
        derives it from the template rather than accepting it from the client.
        """
        self.require_draft("be edited")
        self.category_id = category_id
        self.form_template_id = form_template_id
        self.required_level = required_level
        self.title = title
        self.description = description
        self.visibility = visibility
        self.priority = priority
        self.budget = budget
        self.application_deadline = application_deadline

    def can_accept_applications(self) -> bool:
        return self.status in _APPLICATION_OPEN_STATUSES

    def is_application_deadline_passed(self, at: datetime) -> bool:
        return self.application_deadline is not None and at > self.application_deadline

    def has_supervisor(self) -> bool:
        return self.assigned_supervisor_user_id is not None

    def _ensure_unlocked(self) -> None:
        if self.is_locked():
            raise ProjectLockedError(f"Project {self.id} is locked.")

    def _transition(self, from_status: ProjectStatus, to_status: ProjectStatus) -> None:
        if self.status != from_status:
            raise InvalidProjectStatusTransitionError(
                f"Project {self.id} is '{self.status.value}'; expected '{from_status.value}' "
                f"to transition to '{to_status.value}'."
            )
        self.status = to_status


@dataclass(eq=False)
class ProjectApplication(AggregateRoot):
    project_id: EntityId
    freelancer_profile_id: EntityId
    status: ProjectApplicationStatus
    cover_letter: str | None
    proposed_amount: Decimal | None
    proposed_days: int | None
    applied_at: datetime
    decided_by_user_id: EntityId | None
    decided_at: datetime | None
    decision_note: str | None
    withdrawn_at: datetime | None
    submitted_by_user_id: EntityId | None = None

    def shortlist(self) -> None:
        self._from_applied_or_shortlisted(ProjectApplicationStatus.SHORTLISTED)

    def accept(self, decided_by: EntityId, at: datetime) -> None:
        self._decide(ProjectApplicationStatus.ACCEPTED, decided_by, at, None)

    def reject(self, decided_by: EntityId, at: datetime, note: str | None) -> None:
        self._decide(ProjectApplicationStatus.REJECTED, decided_by, at, note)

    def withdraw(self, at: datetime) -> None:
        if self.status not in (
            ProjectApplicationStatus.APPLIED,
            ProjectApplicationStatus.SHORTLISTED,
        ):
            raise InvalidStateTransitionError(
                f"Application {self.id} is '{self.status.value}' and cannot be withdrawn once decided."
            )
        self.status = ProjectApplicationStatus.WITHDRAWN
        self.withdrawn_at = at

    def _decide(
        self,
        target: ProjectApplicationStatus,
        decided_by: EntityId,
        at: datetime,
        note: str | None,
    ) -> None:
        if self.status in (
            ProjectApplicationStatus.ACCEPTED,
            ProjectApplicationStatus.REJECTED,
        ):
            raise ApplicationAlreadyDecidedError(f"Application {self.id} is already decided as '{self.status.value}'.")
        if self.status not in (
            ProjectApplicationStatus.APPLIED,
            ProjectApplicationStatus.SHORTLISTED,
        ):
            raise InvalidStateTransitionError(f"Application {self.id} is '{self.status.value}' and cannot be decided.")
        self.status = target
        self.decided_by_user_id = decided_by
        self.decided_at = at
        self.decision_note = note

    def _from_applied_or_shortlisted(self, target: ProjectApplicationStatus) -> None:
        if self.status == ProjectApplicationStatus.APPLIED:
            self.status = target
            return
        raise InvalidStateTransitionError(
            f"Application {self.id} is '{self.status.value}'; can only shortlist an APPLIED application."
        )


@dataclass(eq=False)
class ProjectDelivery(AggregateRoot):
    project_id: EntityId
    version_no: int
    submitted_by_user_id: EntityId
    status: DeliveryStatus
    delivery_note: str | None
    submitted_at: datetime
    reviewed_at: datetime | None
    reviewer_user_id: EntityId | None
    superseded_by_delivery_id: EntityId | None
    file_asset_ids: list[EntityId]

    def mark_under_review(self) -> None:
        self._from_reviewable(DeliveryStatus.UNDER_REVIEW)

    def approve(self, reviewer_id: EntityId, at: datetime) -> None:
        self._from_reviewable(DeliveryStatus.APPROVED)
        self.reviewer_user_id = reviewer_id
        self.reviewed_at = at

    def reject(self, reviewer_id: EntityId, at: datetime) -> None:
        self._from_reviewable(DeliveryStatus.REJECTED)
        self.reviewer_user_id = reviewer_id
        self.reviewed_at = at

    def mark_revised(self) -> None:
        self._from_reviewable(DeliveryStatus.REVISED)

    def supersede(self, new_delivery_id: EntityId) -> None:
        if self.status == DeliveryStatus.SUPERSEDED:
            raise InvalidStateTransitionError(f"Delivery {self.id} is already superseded.")
        self.status = DeliveryStatus.SUPERSEDED
        self.superseded_by_delivery_id = new_delivery_id

    def _from_reviewable(self, target: DeliveryStatus) -> None:
        if self.status not in (DeliveryStatus.SUBMITTED, DeliveryStatus.UNDER_REVIEW):
            raise InvalidStateTransitionError(
                f"Delivery {self.id} is '{self.status.value}'; expected SUBMITTED or UNDER_REVIEW."
            )
        self.status = target


@dataclass(eq=False)
class ProjectRevisionRequest(Entity):
    project_id: EntityId
    project_delivery_id: EntityId | None
    requested_by_user_id: EntityId
    requested_to_user_id: EntityId | None
    round_no: int
    status: RevisionRequestStatus
    reason: str
    resolved_by_user_id: EntityId | None
    requested_at: datetime
    resolved_at: datetime | None

    def close(self, resolved_by: EntityId, at: datetime) -> None:
        if self.status != RevisionRequestStatus.OPEN:
            raise InvalidStateTransitionError(
                f"Revision request {self.id} is '{self.status.value}' and cannot be closed."
            )
        self.status = RevisionRequestStatus.CLOSED
        self.resolved_by_user_id = resolved_by
        self.resolved_at = at


@dataclass(eq=False)
class ProjectStatusHistory(Entity):
    project_id: EntityId
    from_status: ProjectStatus | None
    to_status: ProjectStatus
    changed_by_user_id: EntityId
    reason: str | None
    changed_at: datetime
