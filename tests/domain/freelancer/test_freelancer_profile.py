from datetime import UTC, datetime
from decimal import Decimal

import pytest

from app.domain.freelancer.entities import FreelancerProfile
from app.domain.freelancer.enums import FreelancerApprovalStatus
from app.domain.freelancer.exceptions import (
    FreelancerAlreadyApprovedError,
    InvalidRateRangeError,
)
from app.domain.shared.exceptions import InvalidStateTransitionError

NOW = datetime(2026, 8, 2, tzinfo=UTC)


def make_profile(**overrides: object) -> FreelancerProfile:
    fields: dict[str, object] = {
        "id": "profile-1",
        "user_id": "user-1",
        "current_level_id": None,
        "approval_status": FreelancerApprovalStatus.PENDING,
        "approved_by_user_id": None,
        "approved_at": None,
        "approval_note": None,
        "display_name": "Jane Dev",
        "headline": None,
        "bio": None,
        "country_code": None,
        "city": None,
        "timezone": None,
        "hourly_rate_min": None,
        "hourly_rate_max": None,
        "is_available": True,
        "deleted_at": None,
        "created_at": NOW,
    }
    fields.update(overrides)
    return FreelancerProfile(**fields)  # type: ignore[arg-type]


class TestSubmitForApproval:
    def test_pending_profile_can_resubmit(self):
        profile = make_profile()
        profile.submit_for_approval()
        assert profile.approval_status == FreelancerApprovalStatus.PENDING

    def test_rejected_profile_can_resubmit(self):
        profile = make_profile(approval_status=FreelancerApprovalStatus.REJECTED)
        profile.submit_for_approval()
        assert profile.approval_status == FreelancerApprovalStatus.PENDING

    def test_approved_profile_cannot_resubmit(self):
        profile = make_profile(approval_status=FreelancerApprovalStatus.APPROVED)
        with pytest.raises(InvalidStateTransitionError):
            profile.submit_for_approval()

    def test_suspended_profile_cannot_resubmit(self):
        profile = make_profile(approval_status=FreelancerApprovalStatus.SUSPENDED)
        with pytest.raises(InvalidStateTransitionError):
            profile.submit_for_approval()


class TestApprove:
    def test_approve_sets_fields(self):
        profile = make_profile()
        profile.approve("admin-1", NOW, "Looks good")
        assert profile.approval_status == FreelancerApprovalStatus.APPROVED
        assert profile.approved_by_user_id == "admin-1"
        assert profile.approved_at == NOW
        assert profile.approval_note == "Looks good"

    def test_approve_rejected_profile_allowed(self):
        profile = make_profile(approval_status=FreelancerApprovalStatus.REJECTED)
        profile.approve("admin-1", NOW, None)
        assert profile.is_approved()

    def test_double_approve_raises(self):
        profile = make_profile(approval_status=FreelancerApprovalStatus.APPROVED)
        with pytest.raises(FreelancerAlreadyApprovedError):
            profile.approve("admin-1", NOW, None)

    def test_approve_suspended_raises(self):
        profile = make_profile(approval_status=FreelancerApprovalStatus.SUSPENDED)
        with pytest.raises(InvalidStateTransitionError):
            profile.approve("admin-1", NOW, None)


class TestReject:
    def test_reject_pending(self):
        profile = make_profile()
        profile.reject("admin-1", NOW, "Missing portfolio")
        assert profile.approval_status == FreelancerApprovalStatus.REJECTED
        assert profile.approval_note == "Missing portfolio"

    def test_reject_approved_raises(self):
        profile = make_profile(approval_status=FreelancerApprovalStatus.APPROVED)
        with pytest.raises(InvalidStateTransitionError):
            profile.reject("admin-1", NOW, "nope")


class TestSuspend:
    def test_suspend_approved(self):
        profile = make_profile(approval_status=FreelancerApprovalStatus.APPROVED)
        profile.suspend("admin-1", NOW, "Policy violation")
        assert profile.approval_status == FreelancerApprovalStatus.SUSPENDED

    def test_suspend_pending_raises(self):
        profile = make_profile()
        with pytest.raises(InvalidStateTransitionError):
            profile.suspend("admin-1", NOW, "nope")


class TestIsApproved:
    def test_approved_and_not_deleted(self):
        profile = make_profile(approval_status=FreelancerApprovalStatus.APPROVED)
        assert profile.is_approved() is True

    def test_approved_but_deleted(self):
        profile = make_profile(approval_status=FreelancerApprovalStatus.APPROVED, deleted_at=NOW)
        assert profile.is_approved() is False

    def test_pending_is_not_approved(self):
        profile = make_profile()
        assert profile.is_approved() is False


class TestAvailabilityAndLevel:
    def test_set_availability(self):
        profile = make_profile()
        profile.set_availability(False)
        assert profile.is_available is False

    def test_change_level(self):
        profile = make_profile()
        profile.change_level("level-2")
        assert profile.current_level_id == "level-2"


class TestUpdateRateRange:
    def test_valid_range(self):
        profile = make_profile()
        profile.update_rate_range(Decimal("20"), Decimal("40"))
        assert profile.hourly_rate_min == Decimal("20")
        assert profile.hourly_rate_max == Decimal("40")

    def test_invalid_range_raises(self):
        profile = make_profile()
        with pytest.raises(InvalidRateRangeError):
            profile.update_rate_range(Decimal("50"), Decimal("30"))

    def test_clearing_rates_allowed(self):
        profile = make_profile(hourly_rate_min=Decimal("20"), hourly_rate_max=Decimal("40"))
        profile.update_rate_range(None, None)
        assert profile.hourly_rate_min is None
        assert profile.hourly_rate_max is None
