import pytest

from app.application.freelancer.dto import AssignFreelancerLevelCommand
from app.application.freelancer.use_cases.assign_freelancer_level import (
    AssignFreelancerLevelUseCase,
)
from app.application.shared.exceptions import PermissionDeniedError
from app.domain.freelancer.exceptions import FreelancerLevelNotFoundError


def build_use_case(
    authorization_service, profile_repo, level_repo, level_history_repo, id_generator, clock, uow
) -> AssignFreelancerLevelUseCase:
    return AssignFreelancerLevelUseCase(
        authorization_service=authorization_service,
        profile_repo=profile_repo,
        level_repo=level_repo,
        level_history_repo=level_history_repo,
        id_generator=id_generator,
        clock=clock,
        uow=uow,
    )


class TestAssignFreelancerLevelUseCase:
    async def test_assign_level_records_history(
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
        authorization_service.grant("admin", "freelancer.assign_level")
        await make_profile(profile_id="profile-1", current_level_id="level-1")
        make_level(level_id="level-1", level_key="standard")
        make_level(level_id="level-2", level_key="premium", rank_order=2)
        use_case = build_use_case(
            authorization_service,
            profile_repo,
            level_repo,
            level_history_repo,
            id_generator,
            clock,
            uow,
        )

        result = await use_case.execute(
            AssignFreelancerLevelCommand(
                actor_id="admin", profile_id="profile-1", new_level_id="level-2", reason="Promotion"
            )
        )

        assert result.old_level_id == "level-1"
        assert result.new_level_id == "level-2"
        assert (await profile_repo.get_by_id("profile-1")).current_level_id == "level-2"
        history = await level_history_repo.list_by_profile("profile-1")
        assert len(history) == 1
        assert history[0].old_level_id == "level-1"
        assert history[0].new_level_id == "level-2"
        assert history[0].reason == "Promotion"
        assert uow.committed is True

    async def test_requires_permission(
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
        await make_profile(profile_id="profile-1")
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
            await use_case.execute(
                AssignFreelancerLevelCommand(
                    actor_id="admin", profile_id="profile-1", new_level_id="level-2"
                )
            )

    async def test_unknown_level_raises(
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
        authorization_service.grant("admin", "freelancer.assign_level")
        await make_profile(profile_id="profile-1")
        use_case = build_use_case(
            authorization_service,
            profile_repo,
            level_repo,
            level_history_repo,
            id_generator,
            clock,
            uow,
        )

        with pytest.raises(FreelancerLevelNotFoundError):
            await use_case.execute(
                AssignFreelancerLevelCommand(
                    actor_id="admin", profile_id="profile-1", new_level_id="ghost"
                )
            )
