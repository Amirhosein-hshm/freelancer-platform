from fastapi import APIRouter, Depends

from app.application.project.dto import BudgetResult, GetProjectDeliveryQuery, ProjectResult
from app.application.project.use_cases.get_project_delivery import GetProjectDeliveryUseCase
from app.application.review.dto import (
    ApproveDeliveryCommand,
    GetPendingReviewsQuery,
    GetSupervisorProjectsQuery,
    RejectDeliveryCommand,
    ReviewDeliveryCommand,
    ReviewDeliveryResult,
    ReviewResult,
)
from app.application.review.use_cases.approve_delivery import ApproveDeliveryUseCase
from app.application.review.use_cases.get_pending_reviews import GetPendingReviewsUseCase
from app.application.review.use_cases.get_supervisor_projects import GetSupervisorProjectsUseCase
from app.application.review.use_cases.reject_delivery import RejectDeliveryUseCase
from app.application.review.use_cases.review_delivery import ReviewDeliveryUseCase
from app.presentation.api.v1.project.mappers import to_delivery_response
from app.presentation.api.v1.project.schemas import BudgetResponse, DeliveryResponse, ProjectResponse
from app.presentation.api.v1.review.schemas import (
    ApproveDeliveryRequest,
    DeliveryReviewResponse,
    RejectDeliveryRequest,
    ReviewDeliveryRequest,
    ReviewResponse,
)
from app.presentation.core.envelope import PaginationMeta, SuccessEnvelope
from app.presentation.core.pagination import PageQuery
from app.presentation.core.providers import (
    get_approve_delivery_use_case,
    get_get_pending_reviews_use_case,
    get_get_project_delivery_use_case,
    get_get_supervisor_projects_use_case,
    get_reject_delivery_use_case,
    get_review_delivery_use_case,
)
from app.presentation.core.security import get_current_user

router = APIRouter(prefix="/reviews", tags=["Review"])
deliveries_router = APIRouter(prefix="/deliveries", tags=["Review"])


def _to_project_response(result: ProjectResult) -> ProjectResponse:
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
        budget=_to_budget_response(result.budget),
        assigned_supervisor_user_id=result.assigned_supervisor_user_id,
        selected_application_id=result.selected_application_id,
        application_deadline=result.application_deadline,
        created_by_user_id=result.created_by_user_id,
        created_at=result.created_at,
    )


def _to_budget_response(result: BudgetResult) -> BudgetResponse:
    return BudgetResponse(
        budget_type=result.budget_type,
        fixed_amount=result.fixed_amount,
        min_amount=result.min_amount,
        max_amount=result.max_amount,
        currency_code=result.currency_code,
    )


def _to_review_response(result: ReviewResult) -> ReviewResponse:
    return ReviewResponse(
        review_id=result.review_id,
        project_delivery_id=result.project_delivery_id,
        project_id=result.project_id,
        supervisor_user_id=result.supervisor_user_id,
        decision=result.decision,
        reject_reason=result.reject_reason,
        notes=result.notes,
        reviewed_at=result.reviewed_at,
    )


def _to_delivery_review_response(result: ReviewDeliveryResult) -> DeliveryReviewResponse:
    return DeliveryReviewResponse(
        delivery_id=result.delivery_id,
        project_id=result.project_id,
        decision=result.decision,
        project_status=result.project_status,
    )


def _pagination_meta(pagination: PageQuery, total_items: int) -> PaginationMeta:
    return PaginationMeta(
        page=pagination.page,
        page_size=pagination.page_size,
        total_items=total_items,
        total_pages=(total_items + pagination.page_size - 1) // pagination.page_size,
    )


@router.get(
    "/pending",
    response_model=SuccessEnvelope[list[ReviewResponse]],
    operation_id="get_pending_reviews",
)
async def get_pending_reviews(
    current_user=Depends(get_current_user),
    pagination: PageQuery = Depends(),
    use_case: GetPendingReviewsUseCase = Depends(get_get_pending_reviews_use_case),
) -> SuccessEnvelope[list[ReviewResponse]]:
    result = await use_case.execute(GetPendingReviewsQuery(supervisor_user_id=current_user.user_id))
    reviews = [_to_review_response(review) for review in result.reviews]
    return SuccessEnvelope(
        message="Pending reviews.",
        data=reviews,
        meta=_pagination_meta(pagination, len(reviews)),
    )


@router.get(
    "/supervisor/projects",
    response_model=SuccessEnvelope[list[ProjectResponse]],
    operation_id="get_supervisor_projects",
)
async def get_supervisor_projects(
    current_user=Depends(get_current_user),
    pagination: PageQuery = Depends(),
    use_case: GetSupervisorProjectsUseCase = Depends(get_get_supervisor_projects_use_case),
) -> SuccessEnvelope[list[ProjectResponse]]:
    result = await use_case.execute(GetSupervisorProjectsQuery(supervisor_user_id=current_user.user_id))
    projects = [_to_project_response(project) for project in result.projects]
    return SuccessEnvelope(
        message="Supervisor projects.",
        data=projects,
        meta=_pagination_meta(pagination, len(projects)),
    )


@deliveries_router.get(
    "/{delivery_id}",
    response_model=SuccessEnvelope[DeliveryResponse],
    operation_id="get_project_delivery",
)
async def get_project_delivery(
    delivery_id: str,
    current_user=Depends(get_current_user),
    use_case: GetProjectDeliveryUseCase = Depends(get_get_project_delivery_use_case),
) -> SuccessEnvelope[DeliveryResponse]:
    result = await use_case.execute(GetProjectDeliveryQuery(actor_id=current_user.user_id, delivery_id=delivery_id))
    return SuccessEnvelope(
        message="Delivery details.",
        data=to_delivery_response(result),
    )


@deliveries_router.post(
    "/{delivery_id}/review",
    response_model=SuccessEnvelope[DeliveryReviewResponse],
    operation_id="review_delivery",
)
async def review_delivery(
    delivery_id: str,
    payload: ReviewDeliveryRequest,
    current_user=Depends(get_current_user),
    use_case: ReviewDeliveryUseCase = Depends(get_review_delivery_use_case),
) -> SuccessEnvelope[DeliveryReviewResponse]:
    result = await use_case.execute(
        ReviewDeliveryCommand(
            actor_id=current_user.user_id,
            project_delivery_id=delivery_id,
            decision=payload.decision,
            notes=payload.notes,
            reject_reason=payload.reject_reason,
        )
    )
    return SuccessEnvelope(
        message="Delivery reviewed.",
        data=_to_delivery_review_response(result),
    )


@deliveries_router.post(
    "/{delivery_id}/approve",
    response_model=SuccessEnvelope[DeliveryReviewResponse],
    operation_id="approve_delivery",
)
async def approve_delivery(
    delivery_id: str,
    payload: ApproveDeliveryRequest,
    current_user=Depends(get_current_user),
    use_case: ApproveDeliveryUseCase = Depends(get_approve_delivery_use_case),
) -> SuccessEnvelope[DeliveryReviewResponse]:
    result = await use_case.execute(
        ApproveDeliveryCommand(
            actor_id=current_user.user_id,
            project_delivery_id=delivery_id,
            notes=payload.notes,
        )
    )
    return SuccessEnvelope(
        message="Delivery approved.",
        data=_to_delivery_review_response(result),
    )


@deliveries_router.post(
    "/{delivery_id}/reject",
    response_model=SuccessEnvelope[DeliveryReviewResponse],
    operation_id="reject_delivery",
)
async def reject_delivery(
    delivery_id: str,
    payload: RejectDeliveryRequest,
    current_user=Depends(get_current_user),
    use_case: RejectDeliveryUseCase = Depends(get_reject_delivery_use_case),
) -> SuccessEnvelope[DeliveryReviewResponse]:
    result = await use_case.execute(
        RejectDeliveryCommand(
            actor_id=current_user.user_id,
            project_delivery_id=delivery_id,
            reason=payload.reason,
        )
    )
    return SuccessEnvelope(
        message="Delivery rejected.",
        data=_to_delivery_review_response(result),
    )
