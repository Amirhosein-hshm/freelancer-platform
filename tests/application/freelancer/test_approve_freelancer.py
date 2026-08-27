import pytest

from app.application.freelancer.dto import ApproveFreelancerCommand
from app.application.freelancer.use_cases.approve_freelancer import ApproveFreelancerUseCase
from app.application.shared.exceptions import PermissionDeniedError
from app.domain.freelancer.enums import FreelancerApprovalStatus
from app.domain.freelancer.exceptions import FreelancerAlreadyApprovedError


def build_use_case(authorization_service, profile_repo, clock, uow):
    return ApproveFreelancerUseCase(authorization_service, profile_repo, clock, uow)


class TestApproveFreelancerUseCase:
    async def test_approve_does_not_assign_level(self, authorization_service, profile_repo, clock, uow, make_profile):
        authorization_service.grant("admin", "freelancer.approve")
        await make_profile(profile_id="profile-1")
        result = await build_use_case(authorization_service, profile_repo, clock, uow).execute(
            ApproveFreelancerCommand("admin", "profile-1", "OK")
        )
        assert result.approval_status == FreelancerApprovalStatus.APPROVED
        assert result.current_level is None

    async def test_requires_permission(self, authorization_service, profile_repo, clock, uow, make_profile):
        await make_profile(profile_id="profile-1")
        with pytest.raises(PermissionDeniedError):
            await build_use_case(authorization_service, profile_repo, clock, uow).execute(
                ApproveFreelancerCommand("admin", "profile-1")
            )

    async def test_double_approve_raises(self, authorization_service, profile_repo, clock, uow, make_profile):
        authorization_service.grant("admin", "freelancer.approve")
        await make_profile(profile_id="profile-1", approval_status=FreelancerApprovalStatus.APPROVED)
        with pytest.raises(FreelancerAlreadyApprovedError):
            await build_use_case(authorization_service, profile_repo, clock, uow).execute(
                ApproveFreelancerCommand("admin", "profile-1")
            )
