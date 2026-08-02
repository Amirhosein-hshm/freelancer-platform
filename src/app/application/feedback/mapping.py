from app.application.feedback.dto import RatingResult
from app.domain.feedback.entities import Rating


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
