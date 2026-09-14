from app.domain.feedback.entities import CustomerReview, Rating
from app.domain.review.enums import ReviewStatus


def to_domain_customer_review(row: object) -> CustomerReview:
    return CustomerReview(
        id=row.id,
        created_at=row.created_at,
        project_id=row.project_id,
        project_delivery_id=row.project_delivery_id,
        customer_user_id=row.customer_user_id,
        decision=ReviewStatus(row.decision),
        comment=row.comment,
        reviewed_at=row.reviewed_at,
    )


def to_domain_rating(row: object) -> Rating:
    return Rating(
        id=row.id,
        created_at=row.created_at,
        customer_review_id=row.customer_review_id,
        project_id=row.project_id,
        customer_user_id=row.customer_user_id,
        freelancer_profile_id=row.freelancer_profile_id,
        score=row.score,
        comment=row.comment,
        is_public=row.is_public,
    )
