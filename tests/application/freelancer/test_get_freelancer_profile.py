from app.application.freelancer.dto import GetFreelancerProfileQuery
from app.application.freelancer.use_cases.get_freelancer_profile import GetFreelancerProfileUseCase
from app.domain.freelancer.enums import FreelancerApprovalStatus


class TestGetFreelancerProfileUseCase:
    def test_returns_profile(self, profile_repo, make_profile):
        make_profile(profile_id="profile-1", user_id="user-1", city="Tehran")
        use_case = GetFreelancerProfileUseCase(profile_repo=profile_repo)

        result = use_case.execute(GetFreelancerProfileQuery(profile_id="profile-1"))

        assert result.profile_id == "profile-1"
        assert result.user_id == "user-1"
        assert result.city == "Tehran"
        assert result.approval_status == FreelancerApprovalStatus.PENDING
