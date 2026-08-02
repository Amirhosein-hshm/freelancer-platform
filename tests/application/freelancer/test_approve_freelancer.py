import pytest

from app.application.freelancer.dto import ApproveFreelancerCommand
from app.application.freelancer.use_cases.approve_freelancer import (
    DEFAULT_LEVEL_KEY,
    ApproveFreelancerUseCase,
)
from app.application.shared.exceptions import PermissionDeniedError
from app.domain.freelancer.enums import FreelancerApprovalStatus
from app.domain.freelancer.exceptions import FreelancerAlreadyApprovedError


def build_use_case(
    authorization_service, profile_repo, level_repo, level_history_repo, id_generator, clock, uow
) -> ApproveFreelancerUseCase:
    return ApproveFreelancerUseCase(
        authorization_service=authorization_service,
        profile_repo=profile_repo,
        level_repo=level_repo,
        level_history_repo=level_history_repo,
        id_generator=id_generator,
        clock=clock,
        uow=uow,
    )


class TestApproveFreelancerUseCase:
    def test_approve_assigns_default_level_and_history(
        self,
        authorization_service,
        profile_repo,
        level_repo,
        level_history_repo,
        id_generator,
        clock,
        uow,
        make_profile,
        make_level,
    ):
        authorization_service.grant("admin", "freelancer.approve")
        make_profile(profile_id="profile-1")
        make_level(level_id="level-1", level_key=DEFAULT_LEVEL_KEY)
        use_case = build_use_case(
            authorization_service,
            profile_repo,
            level_repo,
            level_history_repo,
            id_generator,
            clock,
            uow,
        )

        result = use_case.execute(
            ApproveFreelancerCommand(actor_id="admin", profile_id="profile-1", note="OK")
        )

        assert result.approval_status == FreelancerApprovalStatus.APPROVED
        assert result.current_level_id == "level-1"
        profile = profile_repo.get_by_id("profile-1")
        assert profile.approved_by_user_id == "admin"
        assert profile.approved_at == clock.now()
        history = level_history_repo.list_by_profile("profile-1")
        assert len(history) == 1
        assert history[0].old_level_id is None
        assert history[0].new_level_id == "level-1"
        assert uow.committed is True

    def test_approve_without_default_level(
        self,
        authorization_service,
        profile_repo,
        level_repo,
        level_history_repo,
        id_generator,
        clock,
        uow,
        make_profile,
    ):
        authorization_service.grant("admin", "freelancer.approve")
        make_profile(profile_id="profile-1")
        use_case = build_use_case(
            authorization_service,
            profile_repo,
            level_repo,
            level_history_repo,
            id_generator,
            clock,
            uow,
        )

        result = use_case.execute(
            ApproveFreelancerCommand(actor_id="admin", profile_id="profile-1")
        )

        assert result.approval_status == FreelancerApprovalStatus.APPROVED
        assert result.current_level_id is None
        assert level_history_repo.list_by_profile("profile-1") == []

    def test_requires_permission(
        self,
        authorization_service,
        profile_repo,
        level_repo,
        level_history_repo,
        id_generator,
        clock,
        uow,
        make_profile,
    ):
        make_profile(profile_id="profile-1")
        use_case = build_use_case(
            authorization_service,
            profile_repo,
            level_repo,
            level_history_repo,
            id_generator,
            clock,
            uow,
        )

        with pytest.raises(PermissionDeniedError):
            use_case.execute(
                ApproveFreelancerCommand(actor_id="admin", profile_id="profile-1")
            )

    def test_double_approve_raises(
        self,
        authorization_service,
        profile_repo,
        level_repo,
        level_history_repo,
        id_generator,
        clock,
        uow,
        make_profile,
    ):
        authorization_service.grant("admin", "freelancer.approve")
        make_profile(profile_id="profile-1", approval_status=FreelancerApprovalStatus.APPROVED)
        use_case = build_use_case(
            authorization_service,
            profile_repo,
            level_repo,
            level_history_repo,
            id_generator,
            clock,
            uow,
        )

        with pytest.raises(FreelancerAlreadyApprovedError):
            use_case.execute(
                ApproveFreelancerCommand(actor_id="admin", profile_id="profile-1")
            )
