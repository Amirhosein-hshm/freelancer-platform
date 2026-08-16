from fastapi import APIRouter, Depends

from app.application.feedback.dto import (
    GetFreelancerRatingsQuery,
    GetProjectRatingQuery,
    RatingResult,
    SubmitRatingCommand,
    SubmitReviewCommand,
)
from app.application.feedback.use_cases.get_freelancer_ratings import GetFreelancerRatingsUseCase
from app.application.feedback.use_cases.get_project_rating import GetProjectRatingUseCase
from app.application.feedback.use_cases.submit_rating import SubmitRatingUseCase
from app.application.feedback.use_cases.submit_review import SubmitReviewUseCase
from app.presentation.api.v1.feedback.schemas import (
    FreelancerRatingsResponse,
    ProjectRatingResponse,
    RatingResponse,
    SubmitRatingRequest,
    SubmitRatingResponse,
    SubmitReviewRequest,
    SubmitReviewResponse,
)
from app.presentation.core.envelope import SuccessEnvelope
from app.presentation.core.providers import (
    get_get_freelancer_ratings_use_case,
    get_get_project_rating_use_case,
    get_submit_rating_use_case,
    get_submit_review_use_case,
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
