from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from app.domain.freelancer.enums import FreelancerApprovalStatus, FreelancerLevelAccessType
from app.domain.freelancer.exceptions import (
    FreelancerAlreadyApprovedError,
    InvalidRateRangeError,
)
from app.domain.shared.entity import AggregateRoot, Entity
from app.domain.shared.exceptions import InvalidStateTransitionError
from app.domain.shared.types import EntityId


@dataclass(eq=False)
class FreelancerLevel(Entity):
    level_key: str
    name: str
    rank_order: int
    access_type: FreelancerLevelAccessType
    min_completed_projects: int
    min_rating: Decimal | None
    max_active_applications: int | None
    can_apply_public_projects: bool
    can_apply_private_projects: bool
    is_active: bool

    def deactivate(self) -> None:
        self.is_active = False


@dataclass(eq=False)
class FreelancerProfile(AggregateRoot):
    user_id: EntityId
    current_level_id: EntityId | None
    approval_status: FreelancerApprovalStatus
    approved_by_user_id: EntityId | None
    approved_at: datetime | None
    approval_note: str | None
    display_name: str
    headline: str | None
    bio: str | None
    country_code: str | None
    city: str | None
    timezone: str | None
    hourly_rate_min: Decimal | None
    hourly_rate_max: Decimal | None
    is_available: bool
    deleted_at: datetime | None

    def submit_for_approval(self) -> None:
        if self.approval_status in (
            FreelancerApprovalStatus.PENDING,
            FreelancerApprovalStatus.REJECTED,
        ):
            self.approval_status = FreelancerApprovalStatus.PENDING
            return
        raise InvalidStateTransitionError(
            f"Freelancer profile {self.id} cannot be submitted for approval from "
            f"status '{self.approval_status.value}'."
        )

    def approve(self, admin_id: EntityId, at: datetime, note: str | None) -> None:
        if self.approval_status == FreelancerApprovalStatus.APPROVED:
            raise FreelancerAlreadyApprovedError(
                f"Freelancer profile {self.id} is already approved."
            )
        if self.approval_status == FreelancerApprovalStatus.SUSPENDED:
            raise InvalidStateTransitionError(
                f"Cannot approve suspended freelancer profile {self.id}."
            )
        self.approval_status = FreelancerApprovalStatus.APPROVED
        self.approved_by_user_id = admin_id
        self.approved_at = at
        self.approval_note = note

    def reject(self, admin_id: EntityId, at: datetime, note: str) -> None:
        if self.approval_status == FreelancerApprovalStatus.APPROVED:
            raise InvalidStateTransitionError(
                f"Cannot reject already approved freelancer profile {self.id}."
            )
        self.approval_status = FreelancerApprovalStatus.REJECTED
        self.approved_by_user_id = admin_id
        self.approved_at = at
        self.approval_note = note

    def suspend(self, admin_id: EntityId, at: datetime, note: str) -> None:
        if self.approval_status != FreelancerApprovalStatus.APPROVED:
            raise InvalidStateTransitionError(
                f"Only approved freelancer profiles can be suspended; profile {self.id} "
                f"is '{self.approval_status.value}'."
            )
        self.approval_status = FreelancerApprovalStatus.SUSPENDED
        self.approved_by_user_id = admin_id
        self.approved_at = at
        self.approval_note = note

    def change_level(self, new_level_id: EntityId) -> None:
        self.current_level_id = new_level_id

    def is_approved(self) -> bool:
        return self.approval_status == FreelancerApprovalStatus.APPROVED and self.deleted_at is None

    def set_availability(self, available: bool) -> None:
        self.is_available = available

    def update_rate_range(self, min_rate: Decimal | None, max_rate: Decimal | None) -> None:
        if min_rate is not None and max_rate is not None and min_rate > max_rate:
            raise InvalidRateRangeError(
                f"Min hourly rate {min_rate} cannot exceed max hourly rate {max_rate}."
            )
        self.hourly_rate_min = min_rate
        self.hourly_rate_max = max_rate


@dataclass(eq=False)
class FreelancerLevelHistory(Entity):
    freelancer_profile_id: EntityId
    old_level_id: EntityId | None
    new_level_id: EntityId
    assigned_by_user_id: EntityId
    reason: str | None
    assigned_at: datetime


@dataclass(eq=False)
class Resume(Entity):
    freelancer_profile_id: EntityId
    file_asset_id: EntityId
    version_no: int
    summary: str | None
    is_current: bool

    def mark_as_current(self) -> None:
        self.is_current = True


@dataclass(eq=False)
class PortfolioItem(Entity):
    freelancer_profile_id: EntityId
    title: str
    description: str | None
    external_url: str | None
    file_asset_id: EntityId | None
    display_order: int
    is_featured: bool
    deleted_at: datetime | None
