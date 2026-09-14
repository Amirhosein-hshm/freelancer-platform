from app.domain.review.entities import SupervisorReview
from app.domain.review.enums import ReviewStatus


def to_domain_supervisor_review(row: object) -> SupervisorReview:
    return SupervisorReview(
        id=row.id,
        created_at=row.created_at,
        updated_at=row.updated_at,
        project_delivery_id=row.project_delivery_id,
        project_id=row.project_id,
        supervisor_user_id=row.supervisor_user_id,
        decision=ReviewStatus(row.decision),
        reject_reason=row.reject_reason,
        notes=row.notes,
        reviewed_at=row.reviewed_at,
    )
