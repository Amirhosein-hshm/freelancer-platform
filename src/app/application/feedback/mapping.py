from app.application.feedback.dto import CustomerReviewResult, RatingResult
from app.domain.feedback.entities import CustomerReview, Rating


def to_review_result(review: CustomerReview) -> CustomerReviewResult:
    return CustomerReviewResult(
        review_id=review.id,
        project_id=review.project_id,
        project_delivery_id=review.project_delivery_id,
        customer_user_id=review.customer_user_id,
        decision=review.decision,
        comment=review.comment,
        reviewed_at=review.reviewed_at,
    )


def to_rating_result(rating: Rating) -> RatingResult:
    return RatingResult(
        rating_id=rating.id,
        customer_review_id=rating.customer_review_id,
        project_id=rating.project_id,
        customer_user_id=rating.customer_user_id,
        freelancer_profile_id=rating.freelancer_profile_id,
        score=rating.score,
        comment=rating.comment,
        is_public=rating.is_public,
    )
