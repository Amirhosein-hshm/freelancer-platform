from datetime import UTC, datetime

import pytest

from app.domain.review.entities import SupervisorReview
from app.domain.review.enums import ReviewStatus
from app.domain.shared.exceptions import InvalidStateTransitionError

NOW = datetime(2026, 8, 2, tzinfo=UTC)


def make_review(decision: ReviewStatus = ReviewStatus.PENDING, **overrides: object) -> SupervisorReview:
    fields: dict[str, object] = {
        "id": "review-1",
        "project_delivery_id": "delivery-1",
        "project_id": "project-1",
        "supervisor_user_id": "supervisor-1",
        "decision": decision,
        "reject_reason": None,
        "notes": None,
        "reviewed_at": None,
        "created_at": NOW,
    }
    fields.update(overrides)
    return SupervisorReview(**fields)  # type: ignore[arg-type]


class TestSupervisorReview:
    def test_defaults_to_pending(self):
        review = make_review()
        assert review.decision == ReviewStatus.PENDING
        assert review.reviewed_at is None

    def test_approve_sets_notes_and_timestamp(self):
        review = make_review()
        review.approve("Looks good", NOW)
        assert review.decision == ReviewStatus.APPROVED
        assert review.notes == "Looks good"
        assert review.reviewed_at == NOW
        assert review.reject_reason is None

    def test_reject_sets_reason_and_timestamp(self):
        review = make_review()
        review.reject("Fails acceptance", NOW)
        assert review.decision == ReviewStatus.REJECTED
        assert review.reject_reason == "Fails acceptance"
        assert review.reviewed_at == NOW

    def test_cannot_approve_twice(self):
        review = make_review()
        review.approve(None, NOW)
        with pytest.raises(InvalidStateTransitionError):
            review.approve("Again", NOW)

    def test_cannot_reject_an_approved_review(self):
        review = make_review()
        review.approve(None, NOW)
        with pytest.raises(InvalidStateTransitionError):
            review.reject("Actually no", NOW)

    def test_identity_based_equality(self):
        assert make_review() == make_review()
        assert make_review() != make_review(id="review-2")
