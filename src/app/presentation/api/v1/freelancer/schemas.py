from decimal import Decimal

from pydantic import BaseModel, Field

from app.domain.freelancer.enums import FreelancerLevelEnum


class CreateFreelancerProfileRequest(BaseModel):
    display_name: str = Field(..., min_length=1)
    headline: str | None = None
    bio: str | None = None
    country_code: str | None = None
    city: str | None = None
    timezone: str | None = None


class AdminCreateFreelancerProfileRequest(BaseModel):
    target_user_id: str
    display_name: str = Field(..., min_length=1)
    headline: str | None = None
    bio: str | None = None
    country_code: str | None = None
    city: str | None = None
    timezone: str | None = None


class UpdateFreelancerProfileRequest(BaseModel):
    display_name: str | None = None
    headline: str | None = None
    bio: str | None = None
    country_code: str | None = None
    city: str | None = None
    timezone: str | None = None
    hourly_rate_min: Decimal | None = None
    hourly_rate_max: Decimal | None = None


class FreelancerProfileResponse(BaseModel):
    profile_id: str
    user_id: str
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
    approval_status: str
    approved_at: str | None


class CreateFreelancerProfileResponse(BaseModel):
    profile_id: str


class SubmitFreelancerApprovalResponse(BaseModel):
    profile_id: str
    approval_status: str


class ApproveFreelancerRequest(BaseModel):
    note: str | None = None


class ApproveFreelancerResponse(BaseModel):
    profile_id: str
    approval_status: str
    current_level: FreelancerLevelEnum | None


class RejectFreelancerRequest(BaseModel):
    note: str


class RejectFreelancerResponse(BaseModel):
    profile_id: str
    approval_status: str


class AssignFreelancerLevelRequest(BaseModel):
    new_level: FreelancerLevelEnum
    reason: str | None = None


class AssignFreelancerLevelResponse(BaseModel):
    profile_id: str
    old_level: FreelancerLevelEnum | None
    new_level: FreelancerLevelEnum


class UploadResumeRequest(BaseModel):
    file_asset_id: str
    summary: str | None = None


class UploadResumeResponse(BaseModel):
    resume_id: str
    version_no: int


class UpdateResumeRequest(BaseModel):
    summary: str | None = None


class UpdateResumeResponse(BaseModel):
    resume_id: str
    summary: str | None


class AddPortfolioItemRequest(BaseModel):
    title: str
    description: str | None = None
    external_url: str | None = None
    file_asset_id: str | None = None
    display_order: int = 0
    is_featured: bool = False


class AddPortfolioItemResponse(BaseModel):
    item_id: str


class UpdatePortfolioItemRequest(BaseModel):
    title: str
    description: str | None = None
    external_url: str | None = None
    file_asset_id: str | None = None
    display_order: int = 0
    is_featured: bool = False


class UpdatePortfolioItemResponse(BaseModel):
    item_id: str


class DeletePortfolioItemResponse(BaseModel):
    item_id: str


class FreelancerLevelHistoryResponse(BaseModel):
    history_id: str
    freelancer_profile_id: str
    old_level: FreelancerLevelEnum | None
    new_level: FreelancerLevelEnum
    assigned_by_user_id: str
    reason: str | None
    assigned_at: str


class ResumeResponse(BaseModel):
    resume_id: str
    freelancer_profile_id: str
    file_asset_id: str
    version_no: int
    summary: str | None
    is_current: bool


class ResumeChangeResponse(BaseModel):
    resume_id: str


class PortfolioItemResponse(BaseModel):
    item_id: str
    freelancer_profile_id: str
    title: str
    description: str | None
    external_url: str | None
    file_asset_id: str | None
    display_order: int
    is_featured: bool
