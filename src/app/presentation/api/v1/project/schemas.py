from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field

from app.domain.freelancer.enums import FreelancerLevelEnum
from app.domain.project.enums import (
    BudgetType,
    DeliveryStatus,
    ProjectApplicationStatus,
    ProjectPriority,
    ProjectStatus,
    ProjectVisibility,
)


class FormValueInputRequest(BaseModel):
    field_id: str
    value: str


class CreateProjectRequest(BaseModel):
    """``category_id`` is derived server-side from the template, so it is not accepted here."""

    form_template_id: str
    title: str
    description: str
    visibility: ProjectVisibility
    budget_type: BudgetType
    currency_code: str
    required_level: FreelancerLevelEnum | None = None
    fixed_budget: Decimal | None = None
    budget_min: Decimal | None = None
    budget_max: Decimal | None = None
    priority: ProjectPriority = ProjectPriority.NORMAL
    application_deadline: datetime | None = None
    form_values: list[FormValueInputRequest] = Field(default_factory=list)


class AdminCreateProjectRequest(BaseModel):
    target_customer_user_id: str
    form_template_id: str
    title: str
    description: str
    visibility: ProjectVisibility
    budget_type: BudgetType
    currency_code: str
    required_level: FreelancerLevelEnum | None = None
    fixed_budget: Decimal | None = None
    budget_min: Decimal | None = None
    budget_max: Decimal | None = None
    priority: ProjectPriority = ProjectPriority.NORMAL
    application_deadline: datetime | None = None
    form_values: list[FormValueInputRequest] = Field(default_factory=list)


class CancelProjectRequest(BaseModel):
    reason: str


class UpdateProjectRequest(BaseModel):
    """DRAFT-only edit; every field is replaced, so send the full desired state.

    ``category_id`` is derived from ``form_template_id`` and is not accepted here.
    """

    form_template_id: str
    title: str
    description: str
    visibility: ProjectVisibility
    budget_type: BudgetType
    currency_code: str
    required_level: FreelancerLevelEnum | None = None
    fixed_budget: Decimal | None = None
    budget_min: Decimal | None = None
    budget_max: Decimal | None = None
    priority: ProjectPriority = ProjectPriority.NORMAL
    application_deadline: datetime | None = None
    form_values: list[FormValueInputRequest] = Field(default_factory=list)


class ApplyForProjectRequest(BaseModel):
    cover_letter: str | None = None
    proposed_amount: Decimal | None = None
    proposed_days: int | None = None


class AdminApplyForProjectRequest(BaseModel):
    target_freelancer_profile_id: str
    cover_letter: str | None = None
    proposed_amount: Decimal | None = None
    proposed_days: int | None = None


class RejectFreelancerRequest(BaseModel):
    note: str | None = None


class SubmitDeliveryRequest(BaseModel):
    delivery_note: str | None = None
    file_asset_ids: list[str] = Field(default_factory=list)


class RequestRevisionRequest(BaseModel):
    reason: str


class BudgetResponse(BaseModel):
    budget_type: BudgetType
    fixed_amount: Decimal | None
    min_amount: Decimal | None
    max_amount: Decimal | None
    currency_code: str


class ProjectResponse(BaseModel):
    project_id: str
    project_code: str
    customer_user_id: str
    category_id: str
    required_level: FreelancerLevelEnum | None
    title: str
    description: str
    status: ProjectStatus
    visibility: ProjectVisibility
    priority: ProjectPriority
    budget: BudgetResponse
    assigned_supervisor_user_id: str | None
    selected_application_id: str | None
    application_deadline: datetime | None
    created_by_user_id: str | None
    created_at: datetime


class ApplicationResponse(BaseModel):
    application_id: str
    project_id: str
    freelancer_profile_id: str
    status: ProjectApplicationStatus
    cover_letter: str | None
    proposed_amount: Decimal | None
    proposed_days: int | None
    applied_at: datetime
    submitted_by_user_id: str | None
    decided_at: datetime | None
    decision_note: str | None


class DeliveryResponse(BaseModel):
    delivery_id: str
    project_id: str
    version_no: int
    status: DeliveryStatus
    delivery_note: str | None
    submitted_at: datetime
    reviewed_at: datetime | None
    reviewer_user_id: str | None
    file_asset_ids: list[str]


class ProjectDetailsResponse(BaseModel):
    project: ProjectResponse
    applications: list[ApplicationResponse]
    deliveries: list[DeliveryResponse]


class CreateProjectResponse(BaseModel):
    project_id: str
    project_code: str
    status: ProjectStatus


class PublishProjectResponse(BaseModel):
    project_id: str
    status: ProjectStatus


class CancelProjectResponse(BaseModel):
    project_id: str
    status: ProjectStatus


class UpdateProjectResponse(BaseModel):
    project_id: str
    status: ProjectStatus


class DeleteProjectResponse(BaseModel):
    project_id: str
    deleted_at: datetime


class ApplyForProjectResponse(BaseModel):
    application_id: str
    status: ProjectApplicationStatus


class AcceptFreelancerResponse(BaseModel):
    project_id: str
    selected_application_id: str
    status: ProjectStatus


class RejectFreelancerResponse(BaseModel):
    application_id: str
    status: ProjectApplicationStatus


class WithdrawApplicationResponse(BaseModel):
    application_id: str
    status: ProjectApplicationStatus


class StartProjectResponse(BaseModel):
    project_id: str
    status: ProjectStatus


class SubmitDeliveryResponse(BaseModel):
    delivery_id: str
    version_no: int
    project_status: ProjectStatus


class RequestRevisionResponse(BaseModel):
    revision_id: str
    round_no: int
    project_status: ProjectStatus


class CompleteProjectResponse(BaseModel):
    project_id: str
    status: ProjectStatus


class ProjectRevisionRequestResponse(BaseModel):
    revision_id: str
    project_id: str
    project_delivery_id: str | None
    requested_by_user_id: str
    requested_to_user_id: str | None
    round_no: int
    status: str
    reason: str
    resolved_by_user_id: str | None
    requested_at: datetime
    resolved_at: datetime | None


class ProjectStatusHistoryResponse(BaseModel):
    history_id: str
    project_id: str
    from_status: str | None
    to_status: str
    changed_by_user_id: str
    reason: str | None
    changed_at: datetime
