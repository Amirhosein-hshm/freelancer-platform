from datetime import UTC, datetime

from app.application.freelancer.dto import FreelancerLevelHistoryResult
from app.domain.freelancer.enums import FreelancerLevelEnum
from app.presentation.api.v1.freelancer.router import _to_history_response


def test_level_history_response_serializes_assigned_at() -> None:
    assigned_at = datetime(2026, 9, 4, 12, 30, tzinfo=UTC)
    result = FreelancerLevelHistoryResult(
        history_id="history-1",
        freelancer_profile_id="profile-1",
        old_level=FreelancerLevelEnum.JUNIOR,
        new_level=FreelancerLevelEnum.MID_LEVEL,
        assigned_by_user_id="admin-1",
        reason="Promotion",
        assigned_at=assigned_at,
    )

    response = _to_history_response(result)

    assert response.assigned_at == assigned_at.isoformat()
