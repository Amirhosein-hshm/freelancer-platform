from decimal import Decimal

import pytest

from app.application.freelancer.dto import UpdateFreelancerProfileCommand
from app.application.freelancer.use_cases.update_freelancer_profile import (
    UpdateFreelancerProfileUseCase,
)
from app.domain.freelancer.exceptions import (
    FreelancerProfileNotFoundError,
    InvalidRateRangeError,
)


def build_use_case(profile_repo) -> UpdateFreelancerProfileUseCase:
    return UpdateFreelancerProfileUseCase(profile_repo=profile_repo)


class TestUpdateFreelancerProfileUseCase:
    def test_update_allowed_fields(self, profile_repo, make_profile):
        make_profile(user_id="user-1")
        use_case = build_use_case(profile_repo)

        result = use_case.execute(
            UpdateFreelancerProfileCommand(
                user_id="user-1",
                display_name="Jane Smith",
                bio="Backend engineer",
                city="Tehran",
                hourly_rate_min=Decimal("20"),
                hourly_rate_max=Decimal("40"),
            )
        )

        assert result.display_name == "Jane Smith"
        assert result.bio == "Backend engineer"
        assert result.city == "Tehran"
        assert result.hourly_rate_min == Decimal("20")
        assert result.hourly_rate_max == Decimal("40")

    def test_partial_rate_update_keeps_other_bound(self, profile_repo, make_profile):
        make_profile(user_id="user-1", hourly_rate_min=Decimal("20"), hourly_rate_max=Decimal("40"))
        use_case = build_use_case(profile_repo)

        result = use_case.execute(
            UpdateFreelancerProfileCommand(user_id="user-1", hourly_rate_max=Decimal("60"))
        )

        assert result.hourly_rate_min == Decimal("20")
        assert result.hourly_rate_max == Decimal("60")

    def test_invalid_rate_range_raises(self, profile_repo, make_profile):
        make_profile(user_id="user-1")
        use_case = build_use_case(profile_repo)

        with pytest.raises(InvalidRateRangeError):
            use_case.execute(
                UpdateFreelancerProfileCommand(
                    user_id="user-1", hourly_rate_min=Decimal("50"), hourly_rate_max=Decimal("30")
                )
            )

    def test_unknown_user_raises(self, profile_repo):
        use_case = build_use_case(profile_repo)

        with pytest.raises(FreelancerProfileNotFoundError):
            use_case.execute(UpdateFreelancerProfileCommand(user_id="ghost", bio="x"))
