from datetime import UTC, datetime
from decimal import Decimal

import pytest

from app.domain.project.entities import ProjectApplication
from app.domain.project.enums import ProjectApplicationStatus
from app.domain.project.exceptions import ApplicationAlreadyDecidedError
from app.domain.shared.exceptions import InvalidStateTransitionError

NOW = datetime(2026, 8, 2, tzinfo=UTC)


def make_application(**overrides: object) -> ProjectApplication:
    fields: dict[str, object] = {
        "id": "app-1",
        "project_id": "project-1",
        "freelancer_profile_id": "profile-1",
        "status": ProjectApplicationStatus.APPLIED,
        "cover_letter": None,
        "proposed_amount": Decimal("800"),
        "proposed_days": 10,
        "applied_at": NOW,
        "decided_by_user_id": None,
        "decided_at": None,
        "decision_note": None,
        "withdrawn_at": None,
        "created_at": NOW,
    }
    fields.update(overrides)
    return ProjectApplication(**fields)  # type: ignore[arg-type]


class TestShortlist:
    def test_applied_to_shortlisted(self):
        app = make_application()
        app.shortlist()
        assert app.status == ProjectApplicationStatus.SHORTLISTED

    def test_shortlist_from_decided_raises(self):
        app = make_application(status=ProjectApplicationStatus.ACCEPTED)
        with pytest.raises(InvalidStateTransitionError):
            app.shortlist()


class TestAccept:
    def test_accept_applied(self):
        app = make_application()
        app.accept("customer-1", NOW)
        assert app.status == ProjectApplicationStatus.ACCEPTED
        assert app.decided_by_user_id == "customer-1"
        assert app.decided_at == NOW

    def test_accept_shortlisted(self):
        app = make_application(status=ProjectApplicationStatus.SHORTLISTED)
        app.accept("customer-1", NOW)
        assert app.status == ProjectApplicationStatus.ACCEPTED

    def test_accept_twice_raises(self):
        app = make_application(status=ProjectApplicationStatus.ACCEPTED)
        with pytest.raises(ApplicationAlreadyDecidedError):
            app.accept("customer-1", NOW)

    def test_accept_rejected_raises(self):
        app = make_application(status=ProjectApplicationStatus.REJECTED)
        with pytest.raises(ApplicationAlreadyDecidedError):
            app.accept("customer-1", NOW)

    def test_accept_withdrawn_raises(self):
        app = make_application(status=ProjectApplicationStatus.WITHDRAWN)
        with pytest.raises(InvalidStateTransitionError):
            app.accept("customer-1", NOW)


class TestReject:
    def test_reject_applied(self):
        app = make_application()
        app.reject("customer-1", NOW, "Not a fit")
        assert app.status == ProjectApplicationStatus.REJECTED
        assert app.decision_note == "Not a fit"

    def test_reject_decided_raises(self):
        app = make_application(status=ProjectApplicationStatus.ACCEPTED)
        with pytest.raises(ApplicationAlreadyDecidedError):
            app.reject("customer-1", NOW, "x")


class TestWithdraw:
    def test_withdraw_applied(self):
        app = make_application()
        app.withdraw(NOW)
        assert app.status == ProjectApplicationStatus.WITHDRAWN
        assert app.withdrawn_at == NOW

    def test_withdraw_accepted_raises(self):
        app = make_application(status=ProjectApplicationStatus.ACCEPTED)
        with pytest.raises(InvalidStateTransitionError):
            app.withdraw(NOW)

    def test_withdraw_twice_raises(self):
        app = make_application(status=ProjectApplicationStatus.WITHDRAWN)
        with pytest.raises(InvalidStateTransitionError):
            app.withdraw(NOW)
