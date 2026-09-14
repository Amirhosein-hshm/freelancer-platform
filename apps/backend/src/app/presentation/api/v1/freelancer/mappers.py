from typing import Any

from app.presentation.api.v1.freelancer.schemas import FreelancerProfileResponse


def to_profile_response(result: Any) -> FreelancerProfileResponse:
    return FreelancerProfileResponse(
        profile_id=result.profile_id,
        user_id=result.user_id,
        display_name=result.display_name,
        headline=result.headline,
        bio=result.bio,
        country_code=result.country_code,
        city=result.city,
        timezone=result.timezone,
        hourly_rate_min=result.hourly_rate_min,
        hourly_rate_max=result.hourly_rate_max,
        is_available=result.is_available,
        current_level=result.current_level,
        approval_status=result.approval_status.value,
        approved_at=result.approved_at.isoformat() if result.approved_at else None,
    )
