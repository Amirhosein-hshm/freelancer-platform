from fastapi import APIRouter, Depends

from app.application.feedback.dto import (
    CustomerReviewResult,
    DeleteCustomerReviewCommand,
    DeleteRatingCommand,
    GetCustomerReviewQuery,
    GetFreelancerRatingsQuery,
    GetProjectRatingQuery,
    ListCustomerReviewsQuery,
    RatingResult,
    SubmitRatingCommand,
    SubmitReviewCommand,
    UpdateCustomerReviewCommand,
    UpdateRatingCommand,
)
from app.application.feedback.use_cases.delete_customer_review import DeleteCustomerReviewUseCase
from app.application.feedback.use_cases.delete_rating import DeleteRatingUseCase
from app.application.feedback.use_cases.get_customer_review import GetCustomerReviewUseCase
from app.application.feedback.use_cases.get_freelancer_ratings import GetFreelancerRatingsUseCase
from app.application.feedback.use_cases.get_project_rating import GetProjectRatingUseCase
from app.application.feedback.use_cases.list_customer_reviews import ListCustomerReviewsUseCase
from app.application.feedback.use_cases.submit_rating import SubmitRatingUseCase
from app.application.feedback.use_cases.submit_review import SubmitReviewUseCase
from app.application.feedback.use_cases.update_customer_review import UpdateCustomerReviewUseCase
from app.application.feedback.use_cases.update_rating import UpdateRatingUseCase
from app.presentation.api.v1.feedback.schemas import (
    CustomerReviewResponse,
    CustomerReviewsResponse,
    FreelancerRatingsResponse,
    ProjectRatingResponse,
    RatingResponse,
    SubmitRatingRequest,
    SubmitRatingResponse,
    SubmitReviewRequest,
    SubmitReviewResponse,
    UpdateCustomerReviewRequest,
    UpdateRatingRequest,
)
from app.presentation.core.envelope import SuccessEnvelope
from app.presentation.core.providers import (
    get_delete_customer_review_use_case,
    get_delete_rating_use_case,
    get_get_customer_review_use_case,
    get_get_freelancer_ratings_use_case,
    get_get_project_rating_use_case,
    get_list_customer_reviews_use_case,
    get_submit_rating_use_case,
    get_submit_review_use_case,
    get_update_customer_review_use_case,
    get_update_rating_use_case,
)
from app.presentation.core.security import get_current_user

router = APIRouter(prefix="/feedback", tags=["Feedback"])


def _to_rating_response(result: RatingResult) -> RatingResponse:
    return RatingResponse(
        rating_id=result.rating_id,
        customer_review_id=result.customer_review_id,
        project_id=result.project_id,
        customer_user_id=result.customer_user_id,
        freelancer_profile_id=result.freelancer_profile_id,
        score=result.score,
        comment=result.comment,
        is_public=result.is_public,
    )


def _to_review_response(result: CustomerReviewResult) -> CustomerReviewResponse:
    return CustomerReviewResponse(
        review_id=result.review_id,
        project_id=result.project_id,
        project_delivery_id=result.project_delivery_id,
        customer_user_id=result.customer_user_id,
        decision=result.decision,
        comment=result.comment,
        reviewed_at=result.reviewed_at,
    )


@router.post(
    "/reviews",
    response_model=SuccessEnvelope[SubmitReviewResponse],
    status_code=201,
    operation_id="submit_review",
)
async def submit_review(
    payload: SubmitReviewRequest,
    current_user=Depends(get_current_user),
    use_case: SubmitReviewUseCase = Depends(get_submit_review_use_case),
) -> SuccessEnvelope[SubmitReviewResponse]:
    result = await use_case.execute(
        SubmitReviewCommand(
            actor_id=current_user.user_id,
            project_id=payload.project_id,
            decision=payload.decision,
            comment=payload.comment,
        )
    )
    return SuccessEnvelope(
        message="Review submitted.",
        data=SubmitReviewResponse(
            review_id=result.review_id,
            project_id=result.project_id,
            decision=result.decision,
            project_status=result.project_status,
        ),
    )


@router.post(
    "/ratings",
    response_model=SuccessEnvelope[SubmitRatingResponse],
    status_code=201,
    operation_id="submit_rating",
)
async def submit_rating(
    payload: SubmitRatingRequest,
    current_user=Depends(get_current_user),
    use_case: SubmitRatingUseCase = Depends(get_submit_rating_use_case),
) -> SuccessEnvelope[SubmitRatingResponse]:
    result = await use_case.execute(
        SubmitRatingCommand(
            actor_id=current_user.user_id,
            project_id=payload.project_id,
            score=payload.score,
            comment=payload.comment,
            is_public=payload.is_public,
        )
    )
    return SuccessEnvelope(
        message="Rating submitted.",
        data=SubmitRatingResponse(
            rating_id=result.rating_id,
            project_id=result.project_id,
            score=result.score,
        ),
    )


@router.get(
    "/projects/{project_id}/rating",
    response_model=SuccessEnvelope[ProjectRatingResponse],
    operation_id="get_project_rating",
)
async def get_project_rating(
    project_id: str,
    current_user=Depends(get_current_user),
    use_case: GetProjectRatingUseCase = Depends(get_get_project_rating_use_case),
) -> SuccessEnvelope[ProjectRatingResponse]:
    result = await use_case.execute(GetProjectRatingQuery(project_id=project_id))
    rating = _to_rating_response(result.rating) if result.rating is not None else None
    return SuccessEnvelope(
        message="Project rating.",
        data=ProjectRatingResponse(rating=rating),
    )


@router.get(
    "/freelancers/{freelancer_profile_id}/ratings",
    response_model=SuccessEnvelope[FreelancerRatingsResponse],
    operation_id="get_freelancer_ratings",
)
async def get_freelancer_ratings(
    freelancer_profile_id: str,
    current_user=Depends(get_current_user),
    use_case: GetFreelancerRatingsUseCase = Depends(get_get_freelancer_ratings_use_case),
) -> SuccessEnvelope[FreelancerRatingsResponse]:
    result = await use_case.execute(GetFreelancerRatingsQuery(freelancer_profile_id=freelancer_profile_id))
    return SuccessEnvelope(
        message="Freelancer ratings.",
        data=FreelancerRatingsResponse(
            ratings=[_to_rating_response(r) for r in result.ratings],
            average_score=result.average_score,
        ),
    )


@router.get(
    "/reviews/{review_id}",
    response_model=SuccessEnvelope[CustomerReviewResponse],
    operation_id="get_customer_review",
)
async def get_customer_review(
    review_id: str,
    current_user=Depends(get_current_user),
    use_case: GetCustomerReviewUseCase = Depends(get_get_customer_review_use_case),
) -> SuccessEnvelope[CustomerReviewResponse]:
    result = await use_case.execute(GetCustomerReviewQuery(actor_id=current_user.user_id, review_id=review_id))
    return SuccessEnvelope(
        message="Customer review details.",
        data=_to_review_response(result.review),
    )


@router.get(
    "/projects/{project_id}/reviews",
    response_model=SuccessEnvelope[CustomerReviewsResponse],
    operation_id="list_customer_reviews",
)
async def list_customer_reviews(
    project_id: str,
    current_user=Depends(get_current_user),
    use_case: ListCustomerReviewsUseCase = Depends(get_list_customer_reviews_use_case),
) -> SuccessEnvelope[CustomerReviewsResponse]:
    result = await use_case.execute(ListCustomerReviewsQuery(actor_id=current_user.user_id, project_id=project_id))
    return SuccessEnvelope(
        message="Customer reviews.",
        data=CustomerReviewsResponse(
            project_id=result.project_id,
            reviews=[_to_review_response(r) for r in result.reviews],
        ),
    )


@router.patch(
    "/reviews/{review_id}",
    response_model=SuccessEnvelope[dict[str, str]],
    operation_id="update_customer_review",
)
async def update_customer_review(
    review_id: str,
    payload: UpdateCustomerReviewRequest,
    current_user=Depends(get_current_user),
    use_case: UpdateCustomerReviewUseCase = Depends(get_update_customer_review_use_case),
) -> SuccessEnvelope[dict[str, str]]:
    result = await use_case.execute(
        UpdateCustomerReviewCommand(
            actor_id=current_user.user_id,
            review_id=review_id,
            comment=payload.comment,
        )
    )
    return SuccessEnvelope(message="Customer review updated.", data={"review_id": result.review_id})


@router.delete(
    "/reviews/{review_id}",
    response_model=SuccessEnvelope[dict[str, str]],
    operation_id="delete_customer_review",
)
async def delete_customer_review(
    review_id: str,
    current_user=Depends(get_current_user),
    use_case: DeleteCustomerReviewUseCase = Depends(get_delete_customer_review_use_case),
) -> SuccessEnvelope[dict[str, str]]:
    await use_case.execute(DeleteCustomerReviewCommand(actor_id=current_user.user_id, review_id=review_id))
    return SuccessEnvelope(message="Customer review deleted.", data={"review_id": review_id})


@router.patch(
    "/ratings/{rating_id}",
    response_model=SuccessEnvelope[dict[str, str]],
    operation_id="update_rating",
)
async def update_rating(
    rating_id: str,
    payload: UpdateRatingRequest,
    current_user=Depends(get_current_user),
    use_case: UpdateRatingUseCase = Depends(get_update_rating_use_case),
) -> SuccessEnvelope[dict[str, str]]:
    result = await use_case.execute(
        UpdateRatingCommand(
            actor_id=current_user.user_id,
            rating_id=rating_id,
            score=payload.score,
            comment=payload.comment,
            is_public=payload.is_public,
        )
    )
    return SuccessEnvelope(message="Rating updated.", data={"rating_id": result.rating_id})


@router.delete(
    "/ratings/{rating_id}",
    response_model=SuccessEnvelope[dict[str, str]],
    operation_id="delete_rating",
)
async def delete_rating(
    rating_id: str,
    current_user=Depends(get_current_user),
    use_case: DeleteRatingUseCase = Depends(get_delete_rating_use_case),
) -> SuccessEnvelope[dict[str, str]]:
    await use_case.execute(DeleteRatingCommand(actor_id=current_user.user_id, rating_id=rating_id))
    return SuccessEnvelope(message="Rating deleted.", data={"rating_id": rating_id})
