from app.application.review.dto import ReviewResult
from app.domain.review.entities import SupervisorReview


def to_review_result(review: SupervisorReview) -> ReviewResult:
    return ReviewResult(
        review_id=review.id,
        project_delivery_id=review.project_delivery_id,
        project_id=review.project_id,
        supervisor_user_id=review.supervisor_user_id,
        decision=review.decision,
        reject_reason=review.reject_reason,
        notes=review.notes,
        reviewed_at=review.reviewed_at,
    )
