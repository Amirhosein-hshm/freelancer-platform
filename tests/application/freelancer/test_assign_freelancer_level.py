import pytest

from app.application.freelancer.dto import AssignFreelancerLevelCommand
from app.application.freelancer.use_cases.assign_freelancer_level import AssignFreelancerLevelUseCase
from app.application.shared.exceptions import PermissionDeniedError
from app.domain.freelancer.enums import FreelancerLevelEnum


def build_use_case(authorization_service, profile_repo, level_history_repo, id_generator, clock, uow):
    return AssignFreelancerLevelUseCase(
        authorization_service, profile_repo, level_history_repo, id_generator, clock, uow
    )


class TestAssignFreelancerLevelUseCase:
    async def test_assign_and_reassign_level_records_history(
        self, authorization_service, profile_repo, level_history_repo, id_generator, clock, uow, make_profile
    ):
        authorization_service.grant("admin", "freelancer.assign_level")
        await make_profile(profile_id="profile-1")
        use_case = build_use_case(authorization_service, profile_repo, level_history_repo, id_generator, clock, uow)

        first = await use_case.execute(
            AssignFreelancerLevelCommand("admin", "profile-1", FreelancerLevelEnum.JUNIOR, "Initial")
        )
        second = await use_case.execute(
            AssignFreelancerLevelCommand("admin", "profile-1", FreelancerLevelEnum.SENIOR, "Promotion")
        )

        assert first.old_level is None
        assert first.new_level == FreelancerLevelEnum.JUNIOR
        assert second.old_level == FreelancerLevelEnum.JUNIOR
        assert second.new_level == FreelancerLevelEnum.SENIOR
        assert (await profile_repo.get_by_id("profile-1")).current_level == FreelancerLevelEnum.SENIOR
        history = await level_history_repo.list_by_profile("profile-1")
        assert [(h.old_level, h.new_level) for h in history] == [
            (None, FreelancerLevelEnum.JUNIOR),
            (FreelancerLevelEnum.JUNIOR, FreelancerLevelEnum.SENIOR),
        ]

    async def test_requires_permission(
        self, authorization_service, profile_repo, level_history_repo, id_generator, clock, uow, make_profile
    ):
        await make_profile(profile_id="profile-1")
        use_case = build_use_case(authorization_service, profile_repo, level_history_repo, id_generator, clock, uow)
        with pytest.raises(PermissionDeniedError):
            await use_case.execute(
                AssignFreelancerLevelCommand("admin", "profile-1", FreelancerLevelEnum.JUNIOR)
            )
