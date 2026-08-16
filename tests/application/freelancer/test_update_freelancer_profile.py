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
    async def test_update_allowed_fields(self, profile_repo, make_profile):
        await make_profile(user_id="user-1")
        use_case = build_use_case(profile_repo)

        result = await use_case.execute(
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

    async def test_update_text_fields_without_rates(self, profile_repo, make_profile):
        await make_profile(user_id="user-1")
        use_case = build_use_case(profile_repo)

        result = await use_case.execute(
            UpdateFreelancerProfileCommand(
                user_id="user-1",
                headline="Senior Python Engineer",
                country_code="IR",
                timezone="Asia/Tehran",
            )
        )

        assert result.headline == "Senior Python Engineer"
        assert result.country_code == "IR"
        assert result.timezone == "Asia/Tehran"
        assert result.hourly_rate_min is None
        assert result.hourly_rate_max is None

    async def test_partial_rate_update_keeps_other_bound(self, profile_repo, make_profile):
        await make_profile(user_id="user-1", hourly_rate_min=Decimal("20"), hourly_rate_max=Decimal("40"))
        use_case = build_use_case(profile_repo)

        result = await use_case.execute(UpdateFreelancerProfileCommand(user_id="user-1", hourly_rate_max=Decimal("60")))

        assert result.hourly_rate_min == Decimal("20")
        assert result.hourly_rate_max == Decimal("60")

    async def test_invalid_rate_range_raises(self, profile_repo, make_profile):
        await make_profile(user_id="user-1")
        use_case = build_use_case(profile_repo)

        with pytest.raises(InvalidRateRangeError):
            await use_case.execute(
                UpdateFreelancerProfileCommand(
                    user_id="user-1", hourly_rate_min=Decimal("50"), hourly_rate_max=Decimal("30")
                )
            )

    async def test_unknown_user_raises(self, profile_repo):
        use_case = build_use_case(profile_repo)

        with pytest.raises(FreelancerProfileNotFoundError):
            await use_case.execute(UpdateFreelancerProfileCommand(user_id="ghost", bio="x"))
