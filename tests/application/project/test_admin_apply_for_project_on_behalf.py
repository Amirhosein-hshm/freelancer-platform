import pytest

from app.application.project.dto import AdminApplyForProjectOnBehalfCommand
from app.application.project.use_cases.admin_apply_for_project_on_behalf import (
    AdminApplyForProjectOnBehalfUseCase,
)
from app.application.shared.exceptions import PermissionDeniedError
from app.domain.freelancer.exceptions import FreelancerProfileNotFoundError
from app.domain.project.entities import ProjectApplication
from app.domain.project.enums import ProjectApplicationStatus, ProjectStatus
from app.domain.project.exceptions import DuplicateApplicationError


def build_on_behalf(
    authorization_service, project_repo, application_repo, profile_repo, level_repo, id_generator, clock, uow
) -> AdminApplyForProjectOnBehalfUseCase:
    return AdminApplyForProjectOnBehalfUseCase(
        authorization_service=authorization_service,
        project_repo=project_repo,
        application_repo=application_repo,
        profile_repo=profile_repo,
        level_repo=level_repo,
        id_generator=id_generator,
        clock=clock,
        uow=uow,
    )


class TestAdminApplyForProjectOnBehalfUseCase:
    async def test_admin_applies_on_behalf_of_target_profile(
        self,
        authorization_service,
        project_repo,
        application_repo,
        profile_repo,
        level_repo,
        id_generator,
        clock,
        uow,
        make_project,
        make_profile,
        make_level,
    ):
        authorization_service.grant("admin-1", "project.apply_on_behalf")
        await make_project(project_id="project-1", status=ProjectStatus.COLLECTING_APPLICATIONS)
        make_level(level_id="level-1")
        await make_profile(profile_id="profile-1", user_id="freelancer-1")
        use_case = build_on_behalf(
            authorization_service, project_repo, application_repo, profile_repo, level_repo, id_generator, clock, uow
        )

        result = await use_case.execute(
            AdminApplyForProjectOnBehalfCommand(
                actor_id="admin-1",
                target_freelancer_profile_id="profile-1",
                project_id="project-1",
            )
        )

        application = await application_repo.get_by_id(result.application_id)
        assert result.status == ProjectApplicationStatus.APPLIED
        assert application.freelancer_profile_id == "profile-1"
        assert application.submitted_by_user_id == "admin-1"
        assert uow.committed is True

    async def test_admin_without_on_behalf_permission_raises(
        self,
        authorization_service,
        project_repo,
        application_repo,
        profile_repo,
        level_repo,
        id_generator,
        clock,
        uow,
    ):
        use_case = build_on_behalf(
            authorization_service, project_repo, application_repo, profile_repo, level_repo, id_generator, clock, uow
        )

        with pytest.raises(PermissionDeniedError):
            await use_case.execute(
                AdminApplyForProjectOnBehalfCommand(
                    actor_id="freelancer-1",
                    target_freelancer_profile_id="profile-1",
                    project_id="project-1",
                )
            )

    async def test_nonexistent_target_profile_raises(
        self,
        authorization_service,
        project_repo,
        application_repo,
        profile_repo,
        level_repo,
        id_generator,
        clock,
        uow,
    ):
        authorization_service.grant("admin-1", "project.apply_on_behalf")
        use_case = build_on_behalf(
            authorization_service, project_repo, application_repo, profile_repo, level_repo, id_generator, clock, uow
        )

        with pytest.raises(FreelancerProfileNotFoundError):
            await use_case.execute(
                AdminApplyForProjectOnBehalfCommand(
                    actor_id="admin-1",
                    target_freelancer_profile_id="missing-profile",
                    project_id="project-1",
                )
            )

    async def test_duplicate_application_for_target_raises(
        self,
        authorization_service,
        project_repo,
        application_repo,
        profile_repo,
        level_repo,
        id_generator,
        clock,
        uow,
        make_project,
        make_profile,
        make_level,
    ):
        authorization_service.grant("admin-1", "project.apply_on_behalf")
        await make_project(project_id="project-1", status=ProjectStatus.COLLECTING_APPLICATIONS)
        make_level(level_id="level-1")
        await make_profile(profile_id="profile-1", user_id="freelancer-1")
        now = await clock.now()
        await application_repo.add(
            ProjectApplication(
                id="app-1",
                project_id="project-1",
                freelancer_profile_id="profile-1",
                status=ProjectApplicationStatus.APPLIED,
                cover_letter=None,
                proposed_amount=None,
                proposed_days=None,
                applied_at=now,
                decided_by_user_id=None,
                decided_at=None,
                decision_note=None,
                withdrawn_at=None,
                created_at=now,
            )
        )
        use_case = build_on_behalf(
            authorization_service, project_repo, application_repo, profile_repo, level_repo, id_generator, clock, uow
        )

        with pytest.raises(DuplicateApplicationError):
            await use_case.execute(
                AdminApplyForProjectOnBehalfCommand(
                    actor_id="admin-1",
                    target_freelancer_profile_id="profile-1",
                    project_id="project-1",
                )
            )

    async def test_self_service_and_on_behalf_share_persisted_state(
        self,
        authorization_service,
        project_repo,
        application_repo,
        profile_repo,
        level_repo,
        id_generator,
        clock,
        uow,
        make_project,
        make_profile,
        make_level,
    ):
        authorization_service.grant("admin-1", "project.apply_on_behalf")
        authorization_service.grant("freelancer-1", "project.apply")
        await make_project(project_id="project-1", status=ProjectStatus.COLLECTING_APPLICATIONS)
        make_level(level_id="level-1")
        await make_profile(profile_id="profile-1", user_id="freelancer-1")

        on_behalf = build_on_behalf(
            authorization_service, project_repo, application_repo, profile_repo, level_repo, id_generator, clock, uow
        )
        result = await on_behalf.execute(
            AdminApplyForProjectOnBehalfCommand(
                actor_id="admin-1",
                target_freelancer_profile_id="profile-1",
                project_id="project-1",
            )
        )

        application = await application_repo.get_by_id(result.application_id)
        assert application.freelancer_profile_id == "profile-1"
        assert application.status == ProjectApplicationStatus.APPLIED
        assert application.project_id == "project-1"
        assert application.submitted_by_user_id == "admin-1"
