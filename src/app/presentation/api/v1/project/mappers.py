from app.application.project.dto import (
    ApplicationResult,
    BudgetResult,
    DeliveryResult,
    ProjectResult,
)
from app.presentation.api.v1.project.schemas import (
    ApplicationResponse,
    BudgetResponse,
    DeliveryResponse,
    ProjectResponse,
)
from app.presentation.core.envelope import PaginationMeta
from app.presentation.core.pagination import PageQuery


def to_budget_response(result: BudgetResult) -> BudgetResponse:
    return BudgetResponse(
        budget_type=result.budget_type,
        fixed_amount=result.fixed_amount,
        min_amount=result.min_amount,
        max_amount=result.max_amount,
        currency_code=result.currency_code,
    )


def to_project_response(result: ProjectResult) -> ProjectResponse:
    return ProjectResponse(
        project_id=result.project_id,
        project_code=result.project_code,
        customer_user_id=result.customer_user_id,
        category_id=result.category_id,
        title=result.title,
        description=result.description,
        status=result.status,
        visibility=result.visibility,
        priority=result.priority,
        budget=to_budget_response(result.budget),
        assigned_supervisor_user_id=result.assigned_supervisor_user_id,
        selected_application_id=result.selected_application_id,
        application_deadline=result.application_deadline,
        created_by_user_id=result.created_by_user_id,
        created_at=result.created_at,
    )


def to_application_response(result: ApplicationResult) -> ApplicationResponse:
    return ApplicationResponse(
        application_id=result.application_id,
        project_id=result.project_id,
        freelancer_profile_id=result.freelancer_profile_id,
        status=result.status,
        cover_letter=result.cover_letter,
        proposed_amount=result.proposed_amount,
        proposed_days=result.proposed_days,
        applied_at=result.applied_at,
        submitted_by_user_id=result.submitted_by_user_id,
        decided_at=result.decided_at,
        decision_note=result.decision_note,
    )


def to_delivery_response(result: DeliveryResult) -> DeliveryResponse:
    return DeliveryResponse(
        delivery_id=result.delivery_id,
        project_id=result.project_id,
        version_no=result.version_no,
        status=result.status,
        delivery_note=result.delivery_note,
        submitted_at=result.submitted_at,
        reviewed_at=result.reviewed_at,
        reviewer_user_id=result.reviewer_user_id,
        file_asset_ids=list(result.file_asset_ids),
    )


def pagination_meta(pagination: PageQuery, total_items: int) -> PaginationMeta:
    return PaginationMeta(
        page=pagination.page,
        page_size=pagination.page_size,
        total_items=total_items,
        total_pages=(total_items + pagination.page_size - 1) // pagination.page_size,
    )
