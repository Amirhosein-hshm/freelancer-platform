from fastapi import APIRouter, Depends

from app.application.project.dto import BudgetResult, GetProjectDeliveryQuery, ProjectResult
from app.application.project.use_cases.get_project_delivery import GetProjectDeliveryUseCase
from app.application.review.dto import (
    GetPendingReviewsQuery,
    GetSupervisorProjectsQuery,
    GetSupervisorReviewQuery,
    ReviewDeliveryCommand,
    ReviewDeliveryResult,
    ReviewResult,
)
from app.application.review.use_cases.get_pending_reviews import GetPendingReviewsUseCase
from app.application.review.use_cases.get_supervisor_projects import GetSupervisorProjectsUseCase
from app.application.review.use_cases.get_supervisor_review import GetSupervisorReviewUseCase
from app.application.review.use_cases.review_delivery import ReviewDeliveryUseCase
from app.application.shared.pagination import total_pages
from app.presentation.api.v1.project.mappers import to_delivery_response
from app.presentation.api.v1.project.schemas import BudgetResponse, DeliveryResponse, ProjectResponse
from app.presentation.api.v1.review.schemas import (
    DeliveryReviewResponse,
    ReviewDeliveryRequest,
    ReviewResponse,
)
from app.presentation.core.envelope import PaginationMeta, SuccessEnvelope
from app.presentation.core.pagination import PageQuery
from app.presentation.core.providers import (
    get_get_pending_reviews_use_case,
    get_get_project_delivery_use_case,
    get_get_supervisor_projects_use_case,
    get_get_supervisor_review_use_case,
    get_review_delivery_use_case,
)
from app.presentation.core.routes import DocumentedAPIRoute
from app.presentation.core.security import get_current_user

router = APIRouter(prefix="/reviews", tags=["Review"], route_class=DocumentedAPIRoute)
deliveries_router = APIRouter(prefix="/deliveries", tags=["Review"], route_class=DocumentedAPIRoute)


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
    result = await use_case.execute(
        GetPendingReviewsQuery(
            actor_id=current_user.user_id,
            supervisor_user_id=current_user.user_id,
            page=pagination.page,
            page_size=pagination.page_size,
        )
    )
    reviews = [_to_review_response(review) for review in result.reviews]
    return SuccessEnvelope(
        message="Pending reviews.",
        data=reviews,
        meta=PaginationMeta(
            page=result.page,
            page_size=result.page_size,
            total_items=result.total_items,
            total_pages=total_pages(result.total_items, result.page_size),
        ),
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
    result = await use_case.execute(
        GetSupervisorProjectsQuery(
            actor_id=current_user.user_id,
            supervisor_user_id=current_user.user_id,
            page=pagination.page,
            page_size=pagination.page_size,
        )
    )
    projects = [_to_project_response(project) for project in result.projects]
    return SuccessEnvelope(
        message="Supervisor projects.",
        data=projects,
        meta=PaginationMeta(
            page=result.page,
            page_size=result.page_size,
            total_items=result.total_items,
            total_pages=total_pages(result.total_items, result.page_size),
        ),
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


@deliveries_router.get(
    "/{delivery_id}/review",
    response_model=SuccessEnvelope[ReviewResponse],
    operation_id="get_supervisor_review",
)
async def get_supervisor_review(
    delivery_id: str,
    current_user=Depends(get_current_user),
    use_case: GetSupervisorReviewUseCase = Depends(get_get_supervisor_review_use_case),
) -> SuccessEnvelope[ReviewResponse]:
    result = await use_case.execute(
        GetSupervisorReviewQuery(actor_id=current_user.user_id, project_delivery_id=delivery_id)
    )
    return SuccessEnvelope(
        message="Supervisor review details.",
        data=_to_review_response(result.review),
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
