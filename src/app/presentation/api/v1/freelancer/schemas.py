from decimal import Decimal

from pydantic import BaseModel, Field


class CreateFreelancerProfileRequest(BaseModel):
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
    current_level_id: str | None
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
    current_level_id: str | None


class RejectFreelancerRequest(BaseModel):
    note: str


class RejectFreelancerResponse(BaseModel):
    profile_id: str
    approval_status: str


class AssignFreelancerLevelRequest(BaseModel):
    new_level_id: str
    reason: str | None = None


class AssignFreelancerLevelResponse(BaseModel):
    profile_id: str
    old_level_id: str | None
    new_level_id: str


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
