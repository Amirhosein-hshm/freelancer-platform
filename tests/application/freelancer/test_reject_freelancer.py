import pytest

from app.application.freelancer.dto import RejectFreelancerCommand
from app.application.freelancer.use_cases.reject_freelancer import RejectFreelancerUseCase
from app.application.shared.exceptions import PermissionDeniedError
from app.domain.freelancer.enums import FreelancerApprovalStatus
from app.domain.shared.exceptions import InvalidStateTransitionError


def build_use_case(authorization_service, profile_repo, clock, uow) -> RejectFreelancerUseCase:
    return RejectFreelancerUseCase(
        authorization_service=authorization_service,
        profile_repo=profile_repo,
        clock=clock,
        uow=uow,
    )


class TestRejectFreelancerUseCase:
    async def test_reject_pending(self, authorization_service, profile_repo, clock, uow, make_profile):
        authorization_service.grant("admin", "freelancer.approve")
        await make_profile(profile_id="profile-1")
        use_case = build_use_case(authorization_service, profile_repo, clock, uow)

        result = await use_case.execute(
            RejectFreelancerCommand(actor_id="admin", profile_id="profile-1", note="No portfolio")
        )

        assert result.approval_status == FreelancerApprovalStatus.REJECTED
        assert (await profile_repo.get_by_id("profile-1")).approval_note == "No portfolio"
        assert uow.committed is True

    async def test_requires_permission(self, authorization_service, profile_repo, clock, uow, make_profile):
        await make_profile(profile_id="profile-1")
        use_case = build_use_case(authorization_service, profile_repo, clock, uow)

        with pytest.raises(PermissionDeniedError):
            await use_case.execute(
                RejectFreelancerCommand(actor_id="admin", profile_id="profile-1", note="x")
            )

    async def test_reject_approved_raises(self, authorization_service, profile_repo, clock, uow, make_profile):
        authorization_service.grant("admin", "freelancer.approve")
        await make_profile(profile_id="profile-1", approval_status=FreelancerApprovalStatus.APPROVED)
        use_case = build_use_case(authorization_service, profile_repo, clock, uow)

        with pytest.raises(InvalidStateTransitionError):
            await use_case.execute(
                RejectFreelancerCommand(actor_id="admin", profile_id="profile-1", note="x")
            )
