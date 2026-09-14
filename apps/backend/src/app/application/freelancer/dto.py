from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal

from app.application.shared.exceptions import ValidationError
from app.application.shared.pagination import DEFAULT_PAGE_SIZE
from app.domain.freelancer.enums import FreelancerApprovalStatus, FreelancerLevelEnum
from app.domain.shared.types import EntityId


@dataclass(frozen=True)
class FreelancerProfileResult:
    profile_id: EntityId
    user_id: EntityId
    display_name: str
    headline: str | None
    bio: str | None
    country_code: str | None
    city: str | None
    timezone: str | None
    hourly_rate_min: Decimal | None
    hourly_rate_max: Decimal | None
    is_available: bool
    current_level: FreelancerLevelEnum | None
    approval_status: FreelancerApprovalStatus
    approved_at: datetime | None


@dataclass(frozen=True)
class CreateFreelancerProfileCommand:
    user_id: EntityId
    display_name: str
    headline: str | None = None
    bio: str | None = None
    country_code: str | None = None
    city: str | None = None
    timezone: str | None = None

    def validate(self) -> None:
        if not self.display_name.strip():
            raise ValidationError("display_name is required.")


@dataclass(frozen=True)
class CreateFreelancerProfileResult:
    profile_id: EntityId


@dataclass(frozen=True)
class CreateFreelancerProfileOnBehalfCommand:
    actor_id: EntityId
    target_user_id: EntityId
    display_name: str
    headline: str | None = None
    bio: str | None = None
    country_code: str | None = None
    city: str | None = None
    timezone: str | None = None

    def validate(self) -> None:
        if not self.display_name.strip():
            raise ValidationError("display_name is required.")


@dataclass(frozen=True)
class UpdateFreelancerProfileCommand:
    user_id: EntityId
    display_name: str | None = None
    headline: str | None = None
    bio: str | None = None
    country_code: str | None = None
    city: str | None = None
    timezone: str | None = None
    hourly_rate_min: Decimal | None = None
    hourly_rate_max: Decimal | None = None

    def validate(self) -> None:
        if self.display_name is not None and not self.display_name.strip():
            raise ValidationError("display_name cannot be empty.")


@dataclass(frozen=True)
class UploadResumeCommand:
    user_id: EntityId
    file_asset_id: EntityId
    summary: str | None = None


@dataclass(frozen=True)
class UploadResumeResult:
    resume_id: EntityId
    version_no: int


@dataclass(frozen=True)
class UpdateResumeCommand:
    user_id: EntityId
    summary: str | None = None


@dataclass(frozen=True)
class UpdateResumeResult:
    resume_id: EntityId
    summary: str | None


@dataclass(frozen=True)
class AddPortfolioItemCommand:
    user_id: EntityId
    title: str
    description: str | None = None
    external_url: str | None = None
    file_asset_id: EntityId | None = None
    display_order: int = 0
    is_featured: bool = False

    def validate(self) -> None:
        if not self.title.strip():
            raise ValidationError("title is required.")


@dataclass(frozen=True)
class AddPortfolioItemResult:
    item_id: EntityId


@dataclass(frozen=True)
class UpdatePortfolioItemCommand:
    user_id: EntityId
    item_id: EntityId
    title: str
    description: str | None = None
    external_url: str | None = None
    file_asset_id: EntityId | None = None
    display_order: int = 0
    is_featured: bool = False

    def validate(self) -> None:
        if not self.title.strip():
            raise ValidationError("title is required.")


@dataclass(frozen=True)
class UpdatePortfolioItemResult:
    item_id: EntityId


@dataclass(frozen=True)
class DeletePortfolioItemCommand:
    user_id: EntityId
    item_id: EntityId


@dataclass(frozen=True)
class DeletePortfolioItemResult:
    item_id: EntityId


@dataclass(frozen=True)
class SubmitFreelancerApprovalCommand:
    user_id: EntityId


@dataclass(frozen=True)
class SubmitFreelancerApprovalResult:
    profile_id: EntityId
    approval_status: FreelancerApprovalStatus


@dataclass(frozen=True)
class ApproveFreelancerCommand:
    actor_id: EntityId
    profile_id: EntityId
    note: str | None = None


@dataclass(frozen=True)
class ApproveFreelancerResult:
    profile_id: EntityId
    approval_status: FreelancerApprovalStatus
    current_level: FreelancerLevelEnum | None


@dataclass(frozen=True)
class RejectFreelancerCommand:
    actor_id: EntityId
    profile_id: EntityId
    note: str


@dataclass(frozen=True)
class RejectFreelancerResult:
    profile_id: EntityId
    approval_status: FreelancerApprovalStatus


@dataclass(frozen=True)
class AssignFreelancerLevelCommand:
    actor_id: EntityId
    profile_id: EntityId
    new_level: FreelancerLevelEnum
    reason: str | None = None


@dataclass(frozen=True)
class AssignFreelancerLevelResult:
    profile_id: EntityId
    old_level: FreelancerLevelEnum | None
    new_level: FreelancerLevelEnum


@dataclass(frozen=True)
class GetFreelancerProfileQuery:
    profile_id: EntityId


@dataclass(frozen=True)
class ListFreelancerProfilesByApprovalStatusQuery:
    actor_id: EntityId
    status: FreelancerApprovalStatus
    page: int = 1
    page_size: int = DEFAULT_PAGE_SIZE


@dataclass(frozen=True)
class ListFreelancerProfilesByApprovalStatusResult:
    profiles: list[FreelancerProfileResult]
    total_items: int
    page: int
    page_size: int


@dataclass(frozen=True)
class SoftDeleteFreelancerProfileCommand:
    actor_id: EntityId
    profile_id: EntityId


@dataclass(frozen=True)
class SoftDeleteFreelancerProfileResult:
    profile_id: EntityId


@dataclass(frozen=True)
class ListFreelancerLevelHistoryQuery:
    actor_id: EntityId
    profile_id: EntityId
    page: int = 1
    page_size: int = DEFAULT_PAGE_SIZE


@dataclass(frozen=True)
class FreelancerLevelHistoryResult:
    history_id: EntityId
    freelancer_profile_id: EntityId
    old_level: FreelancerLevelEnum | None
    new_level: FreelancerLevelEnum
    assigned_by_user_id: EntityId
    reason: str | None
    assigned_at: datetime


@dataclass(frozen=True)
class ListFreelancerLevelHistoryResult:
    history: list[FreelancerLevelHistoryResult]
    total_items: int
    page: int
    page_size: int


@dataclass(frozen=True)
class ResumeResult:
    resume_id: EntityId
    freelancer_profile_id: EntityId
    file_asset_id: EntityId
    version_no: int
    summary: str | None
    is_current: bool


@dataclass(frozen=True)
class GetResumeQuery:
    actor_id: EntityId
    resume_id: EntityId


@dataclass(frozen=True)
class GetCurrentResumeQuery:
    actor_id: EntityId
    profile_id: EntityId


@dataclass(frozen=True)
class ListResumeVersionsQuery:
    actor_id: EntityId
    profile_id: EntityId
    page: int = 1
    page_size: int = DEFAULT_PAGE_SIZE


@dataclass(frozen=True)
class ListResumeVersionsResult:
    resumes: list[ResumeResult]
    total_items: int
    page: int
    page_size: int


@dataclass(frozen=True)
class SetCurrentResumeCommand:
    actor_id: EntityId
    profile_id: EntityId
    resume_id: EntityId


@dataclass(frozen=True)
class SetCurrentResumeResult:
    resume_id: EntityId


@dataclass(frozen=True)
class DeleteResumeCommand:
    actor_id: EntityId
    profile_id: EntityId
    resume_id: EntityId


@dataclass(frozen=True)
class DeleteResumeResult:
    resume_id: EntityId


@dataclass(frozen=True)
class PortfolioItemResult:
    item_id: EntityId
    freelancer_profile_id: EntityId
    title: str
    description: str | None
    external_url: str | None
    file_asset_id: EntityId | None
    display_order: int
    is_featured: bool
    deleted_at: datetime | None


@dataclass(frozen=True)
class GetPortfolioItemQuery:
    actor_id: EntityId
    item_id: EntityId


@dataclass(frozen=True)
class ListPortfolioItemsQuery:
    actor_id: EntityId
    profile_id: EntityId
    page: int = 1
    page_size: int = DEFAULT_PAGE_SIZE


@dataclass(frozen=True)
class ListPortfolioItemsResult:
    items: list[PortfolioItemResult]
    total_items: int
    page: int
    page_size: int