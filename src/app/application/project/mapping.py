from app.application.project.dto import (
    ApplicationResult,
    BudgetResult,
    DeliveryResult,
    ProjectResult,
)
from app.domain.project.entities import Project, ProjectApplication, ProjectDelivery


def to_budget_result(project: Project) -> BudgetResult:
    return BudgetResult(
        budget_type=project.budget.budget_type,
        fixed_amount=project.budget.fixed_amount,
        min_amount=project.budget.min_amount,
        max_amount=project.budget.max_amount,
        currency_code=project.budget.currency_code,
    )


def to_project_result(project: Project) -> ProjectResult:
    return ProjectResult(
        project_id=project.id,
        project_code=project.project_code.value,
        customer_user_id=project.customer_user_id,
        category_id=project.category_id,
        title=project.title,
        description=project.description,
        status=project.status,
        visibility=project.visibility,
        priority=project.priority,
        budget=to_budget_result(project),
        assigned_supervisor_user_id=project.assigned_supervisor_user_id,
        selected_application_id=project.selected_application_id,
        application_deadline=project.application_deadline,
        created_at=project.created_at,
    )


def to_application_result(application: ProjectApplication) -> ApplicationResult:
    return ApplicationResult(
        application_id=application.id,
        project_id=application.project_id,
        freelancer_profile_id=application.freelancer_profile_id,
        status=application.status,
        cover_letter=application.cover_letter,
        proposed_amount=application.proposed_amount,
        proposed_days=application.proposed_days,
        applied_at=application.applied_at,
        submitted_by_user_id=application.submitted_by_user_id,
        decided_at=application.decided_at,
        decision_note=application.decision_note,
    )


def to_delivery_result(delivery: ProjectDelivery) -> DeliveryResult:
    return DeliveryResult(
        delivery_id=delivery.id,
        project_id=delivery.project_id,
        version_no=delivery.version_no,
        status=delivery.status,
        delivery_note=delivery.delivery_note,
        submitted_at=delivery.submitted_at,
        reviewed_at=delivery.reviewed_at,
        reviewer_user_id=delivery.reviewer_user_id,
        file_asset_ids=list(delivery.file_asset_ids),
    )
