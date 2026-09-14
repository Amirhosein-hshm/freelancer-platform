from datetime import UTC, datetime

import pytest

from app.domain.project.entities import ProjectDelivery, ProjectRevisionRequest
from app.domain.project.enums import DeliveryStatus, RevisionRequestStatus
from app.domain.shared.exceptions import InvalidStateTransitionError

NOW = datetime(2026, 8, 2, tzinfo=UTC)


def make_delivery(**overrides: object) -> ProjectDelivery:
    fields: dict[str, object] = {
        "id": "delivery-1",
        "project_id": "project-1",
        "version_no": 1,
        "submitted_by_user_id": "freelancer-1",
        "status": DeliveryStatus.SUBMITTED,
        "delivery_note": None,
        "submitted_at": NOW,
        "reviewed_at": None,
        "reviewer_user_id": None,
        "superseded_by_delivery_id": None,
        "file_asset_ids": [],
        "created_at": NOW,
    }
    fields.update(overrides)
    return ProjectDelivery(**fields)  # type: ignore[arg-type]


class TestDeliveryStatusTransitions:
    def test_mark_under_review(self):
        delivery = make_delivery()
        delivery.mark_under_review()
        assert delivery.status == DeliveryStatus.UNDER_REVIEW

    def test_approve(self):
        delivery = make_delivery()
        delivery.approve("supervisor-1", NOW)
        assert delivery.status == DeliveryStatus.APPROVED
        assert delivery.reviewer_user_id == "supervisor-1"
        assert delivery.reviewed_at == NOW

    def test_reject(self):
        delivery = make_delivery()
        delivery.reject("supervisor-1", NOW)
        assert delivery.status == DeliveryStatus.REJECTED

    def test_approve_from_under_review(self):
        delivery = make_delivery(status=DeliveryStatus.UNDER_REVIEW)
        delivery.approve("supervisor-1", NOW)
        assert delivery.status == DeliveryStatus.APPROVED

    def test_approve_after_approved_raises(self):
        delivery = make_delivery(status=DeliveryStatus.APPROVED)
        with pytest.raises(InvalidStateTransitionError):
            delivery.approve("supervisor-1", NOW)

    def test_mark_revised(self):
        delivery = make_delivery(status=DeliveryStatus.UNDER_REVIEW)
        delivery.mark_revised()
        assert delivery.status == DeliveryStatus.REVISED

    def test_supersede(self):
        delivery = make_delivery()
        delivery.supersede("delivery-2")
        assert delivery.status == DeliveryStatus.SUPERSEDED
        assert delivery.superseded_by_delivery_id == "delivery-2"

    def test_supersede_twice_raises(self):
        delivery = make_delivery(status=DeliveryStatus.SUPERSEDED)
        with pytest.raises(InvalidStateTransitionError):
            delivery.supersede("delivery-3")


def make_revision(**overrides: object) -> ProjectRevisionRequest:
    fields: dict[str, object] = {
        "id": "revision-1",
        "project_id": "project-1",
        "project_delivery_id": "delivery-1",
        "requested_by_user_id": "supervisor-1",
        "requested_to_user_id": "freelancer-1",
        "round_no": 1,
        "status": RevisionRequestStatus.OPEN,
        "reason": "Fix the auth flow",
        "resolved_by_user_id": None,
        "requested_at": NOW,
        "resolved_at": None,
        "created_at": NOW,
    }
    fields.update(overrides)
    return ProjectRevisionRequest(**fields)  # type: ignore[arg-type]


class TestRevisionClose:
    def test_close_open(self):
        revision = make_revision()
        revision.close("freelancer-1", NOW)
        assert revision.status == RevisionRequestStatus.CLOSED
        assert revision.resolved_by_user_id == "freelancer-1"
        assert revision.resolved_at == NOW

    def test_close_closed_raises(self):
        revision = make_revision(status=RevisionRequestStatus.CLOSED)
        with pytest.raises(InvalidStateTransitionError):
            revision.close("freelancer-1", NOW)
