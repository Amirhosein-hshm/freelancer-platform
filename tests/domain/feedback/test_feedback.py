from datetime import UTC, datetime

import pytest

from app.domain.feedback.entities import CustomerReview, Rating
from app.domain.feedback.exceptions import InvalidRatingScoreError
from app.domain.review.enums import ReviewStatus

NOW = datetime(2026, 8, 2, tzinfo=UTC)


def make_review(**overrides: object) -> CustomerReview:
    fields: dict[str, object] = {
        "id": "review-1",
        "project_id": "project-1",
        "project_delivery_id": "delivery-1",
        "customer_user_id": "customer-1",
        "decision": ReviewStatus.APPROVED,
        "comment": None,
        "reviewed_at": NOW,
        "created_at": NOW,
    }
    fields.update(overrides)
    return CustomerReview(**fields)  # type: ignore[arg-type]


def make_rating(score: int = 5, **overrides: object) -> Rating:
    fields: dict[str, object] = {
        "id": "rating-1",
        "customer_review_id": "review-1",
        "project_id": "project-1",
        "customer_user_id": "customer-1",
        "freelancer_profile_id": "profile-1",
        "score": score,
        "comment": None,
        "is_public": False,
        "created_at": NOW,
    }
    fields.update(overrides)
    return Rating(**fields)  # type: ignore[arg-type]


class TestCustomerReview:
    def test_stores_decision_and_comment(self):
        review = make_review(comment="Great work", decision=ReviewStatus.REJECTED)
        assert review.decision == ReviewStatus.REJECTED
        assert review.comment == "Great work"


class TestRating:
    @pytest.mark.parametrize("score", [1, 3, 5])
    def test_valid_scores_accepted(self, score):
        rating = make_rating(score=score)
        assert rating.score == score

    @pytest.mark.parametrize("score", [0, -1, 6, 100])
    def test_invalid_scores_rejected(self, score):
        with pytest.raises(InvalidRatingScoreError):
            make_rating(score=score)

    def test_identity_based_equality(self):
        assert make_rating() == make_rating()
        assert make_rating() != make_rating(id="rating-2")
