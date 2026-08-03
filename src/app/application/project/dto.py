from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal

from app.application.shared.exceptions import ValidationError
from app.domain.project.enums import (
    BudgetType,
    DeliveryStatus,
    ProjectApplicationStatus,
    ProjectPriority,
    ProjectStatus,
    ProjectVisibility,
)
from app.domain.shared.types import EntityId


@dataclass(frozen=True)
class FormValueInput:
    field_id: EntityId
    value: str


@dataclass(frozen=True)
class BudgetResult:
    budget_type: BudgetType
    fixed_amount: Decimal | None
    min_amount: Decimal | None
    max_amount: Decimal | None
    currency_code: str


@dataclass(frozen=True)
class ProjectResult:
    project_id: EntityId
    project_code: str
    customer_user_id: EntityId
    category_id: EntityId
    title: str
    description: str
    status: ProjectStatus
    visibility: ProjectVisibility
    priority: ProjectPriority
    budget: BudgetResult
    assigned_supervisor_user_id: EntityId | None
    selected_application_id: EntityId | None
    application_deadline: datetime | None
    created_at: datetime


@dataclass(frozen=True)
class ApplicationResult:
    application_id: EntityId
    project_id: EntityId
    freelancer_profile_id: EntityId
    status: ProjectApplicationStatus
    cover_letter: str | None
    proposed_amount: Decimal | None
    proposed_days: int | None
    applied_at: datetime
    submitted_by_user_id: EntityId | None
    decided_at: datetime | None
    decision_note: str | None


@dataclass(frozen=True)
class DeliveryResult:
    delivery_id: EntityId
    project_id: EntityId
    version_no: int
    status: DeliveryStatus
    delivery_note: str | None
    submitted_at: datetime
    reviewed_at: datetime | None
    reviewer_user_id: EntityId | None
    file_asset_ids: list[EntityId]


@dataclass(frozen=True)
class CreateProjectCommand:
    actor_id: EntityId
    customer_user_id: EntityId
    category_id: EntityId
    title: str
    description: str
    visibility: ProjectVisibility
    budget_type: BudgetType
    currency_code: str
    fixed_budget: Decimal | None = None
    budget_min: Decimal | None = None
    budget_max: Decimal | None = None
    priority: ProjectPriority = ProjectPriority.NORMAL
    application_deadline: datetime | None = None
    form_values: list[FormValueInput] = field(default_factory=list)

    def validate(self) -> None:
        if not self.title.strip() or not self.description.strip():
            raise ValidationError("title and description are required.")
        if not self.currency_code.strip():
            raise ValidationError("currency_code is required.")


@dataclass(frozen=True)
class CreateProjectResult:
    project_id: EntityId
    project_code: str
    status: ProjectStatus


@dataclass(frozen=True)
class PublishProjectCommand:
    actor_id: EntityId
    project_id: EntityId


@dataclass(frozen=True)
class PublishProjectResult:
    project_id: EntityId
    status: ProjectStatus


@dataclass(frozen=True)
class CancelProjectCommand:
    actor_id: EntityId
    project_id: EntityId
    reason: str


@dataclass(frozen=True)
class CancelProjectResult:
    project_id: EntityId
    status: ProjectStatus


@dataclass(frozen=True)
class ApplyForProjectCommand:
    actor_id: EntityId
    project_id: EntityId
    cover_letter: str | None = None
    proposed_amount: Decimal | None = None
    proposed_days: int | None = None


@dataclass(frozen=True)
class ApplyForProjectResult:
    application_id: EntityId
    status: ProjectApplicationStatus


@dataclass(frozen=True)
class WithdrawApplicationCommand:
    actor_id: EntityId
    application_id: EntityId


@dataclass(frozen=True)
class WithdrawApplicationResult:
    application_id: EntityId
    status: ProjectApplicationStatus


@dataclass(frozen=True)
class ViewApplicationsQuery:
    actor_id: EntityId
    project_id: EntityId


@dataclass(frozen=True)
class ViewApplicationsResult:
    project_id: EntityId
    applications: list[ApplicationResult]


@dataclass(frozen=True)
class AcceptFreelancerCommand:
    actor_id: EntityId
    application_id: EntityId


@dataclass(frozen=True)
class AcceptFreelancerResult:
    project_id: EntityId
    selected_application_id: EntityId
    status: ProjectStatus


@dataclass(frozen=True)
class RejectFreelancerCommand:
    actor_id: EntityId
    application_id: EntityId
    note: str | None = None


@dataclass(frozen=True)
class RejectFreelancerResult:
    application_id: EntityId
    status: ProjectApplicationStatus


@dataclass(frozen=True)
class StartProjectCommand:
    actor_id: EntityId
    project_id: EntityId


@dataclass(frozen=True)
class StartProjectResult:
    project_id: EntityId
    status: ProjectStatus


@dataclass(frozen=True)
class SubmitDeliveryCommand:
    actor_id: EntityId
    project_id: EntityId
    delivery_note: str | None = None
    file_asset_ids: list[EntityId] = field(default_factory=list)


@dataclass(frozen=True)
class SubmitDeliveryResult:
    delivery_id: EntityId
    version_no: int
    project_status: ProjectStatus


@dataclass(frozen=True)
class RequestRevisionCommand:
    actor_id: EntityId
    project_id: EntityId
    reason: str


@dataclass(frozen=True)
class RequestRevisionResult:
    revision_id: EntityId
    round_no: int
    project_status: ProjectStatus


@dataclass(frozen=True)
class CompleteProjectCommand:
    actor_id: EntityId
    project_id: EntityId


@dataclass(frozen=True)
class CompleteProjectResult:
    project_id: EntityId
    status: ProjectStatus


@dataclass(frozen=True)
class GetProjectDetailsQuery:
    project_id: EntityId


@dataclass(frozen=True)
class GetProjectDetailsResult:
    project: ProjectResult
    applications: list[ApplicationResult]
    deliveries: list[DeliveryResult]


@dataclass(frozen=True)
class GetMyProjectsQuery:
    customer_user_id: EntityId


@dataclass(frozen=True)
class GetMyProjectsResult:
    projects: list[ProjectResult]


@dataclass(frozen=True)
class GetAvailableProjectsQuery:
    actor_id: EntityId


@dataclass(frozen=True)
class GetAvailableProjectsResult:
    projects: list[ProjectResult]
