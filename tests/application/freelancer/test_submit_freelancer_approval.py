import pytest

from app.application.freelancer.dto import SubmitFreelancerApprovalCommand
from app.application.freelancer.use_cases.submit_freelancer_approval import (
    SubmitFreelancerApprovalUseCase,
)
from app.domain.freelancer.enums import FreelancerApprovalStatus
from app.domain.shared.exceptions import InvalidStateTransitionError


def build_use_case(profile_repo, uow) -> SubmitFreelancerApprovalUseCase:
    return SubmitFreelancerApprovalUseCase(profile_repo=profile_repo, uow=uow)


class TestSubmitFreelancerApprovalUseCase:
    def test_pending_profile_can_submit(self, profile_repo, uow, make_profile):
        make_profile(user_id="user-1")
        use_case = build_use_case(profile_repo, uow)

        result = use_case.execute(SubmitFreelancerApprovalCommand(user_id="user-1"))

        assert result.profile_id == "profile-1"
        assert result.approval_status == FreelancerApprovalStatus.PENDING
        assert uow.committed is True

    def test_rejected_profile_resubmits(self, profile_repo, uow, make_profile):
        make_profile(user_id="user-1", approval_status=FreelancerApprovalStatus.REJECTED)
        use_case = build_use_case(profile_repo, uow)

        result = use_case.execute(SubmitFreelancerApprovalCommand(user_id="user-1"))

        assert result.approval_status == FreelancerApprovalStatus.PENDING

    def test_approved_profile_cannot_submit(self, profile_repo, uow, make_profile):
        make_profile(user_id="user-1", approval_status=FreelancerApprovalStatus.APPROVED)
        use_case = build_use_case(profile_repo, uow)

        with pytest.raises(InvalidStateTransitionError):
            use_case.execute(SubmitFreelancerApprovalCommand(user_id="user-1"))
