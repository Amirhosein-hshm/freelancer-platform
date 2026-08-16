from datetime import UTC, datetime
from decimal import Decimal

import pytest

from app.application.project.dto import (
    ApplyForProjectCommand,
    WithdrawApplicationCommand,
)
from app.application.project.use_cases.apply_for_project import ApplyForProjectUseCase
from app.application.project.use_cases.withdraw_application import WithdrawApplicationUseCase
from app.application.shared.exceptions import PermissionDeniedError
from app.domain.freelancer.enums import FreelancerApprovalStatus
from app.domain.freelancer.exceptions import FreelancerNotApprovedError
from app.domain.project.entities import ProjectApplication
from app.domain.project.enums import ProjectApplicationStatus, ProjectStatus
from app.domain.project.exceptions import (
    ApplicationDeadlineExpiredError,
    DuplicateApplicationError,
    FreelancerNotEligibleError,
)


def build_apply(
    authorization_service, project_repo, application_repo, profile_repo, level_repo, id_generator, clock, uow
) -> ApplyForProjectUseCase:
    return ApplyForProjectUseCase(
        authorization_service=authorization_service,
        project_repo=project_repo,
        application_repo=application_repo,
        profile_repo=profile_repo,
        level_repo=level_repo,
        id_generator=id_generator,
        clock=clock,
        uow=uow,
    )


async def seed_application(
    application_repo, app_id: str = "app-1", project_id: str = "project-1", **overrides: object
) -> ProjectApplication:
    fields: dict[str, object] = {
        "id": app_id,
        "project_id": project_id,
        "freelancer_profile_id": "profile-1",
        "status": ProjectApplicationStatus.APPLIED,
        "cover_letter": None,
        "proposed_amount": Decimal("800"),
        "proposed_days": 10,
        "applied_at": None,
        "decided_by_user_id": None,
        "decided_at": None,
        "decision_note": None,
        "withdrawn_at": None,
        "created_at": None,
    }
    fields.update(overrides)
    return await application_repo.add(ProjectApplication(**fields))  # type: ignore[arg-type]


class TestApplyForProjectUseCase:
    async def test_apply_succeeds(
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
        authorization_service.grant("freelancer-1", "project.apply")
        await make_project(project_id="project-1", status=ProjectStatus.COLLECTING_APPLICATIONS)
        await make_level(level_id="level-1", max_active_applications=3)
        await make_profile(profile_id="profile-1", user_id="freelancer-1")
        use_case = build_apply(
            authorization_service, project_repo, application_repo, profile_repo, level_repo, id_generator, clock, uow
        )

        result = await use_case.execute(
            ApplyForProjectCommand(
                actor_id="freelancer-1",
                project_id="project-1",
                proposed_amount=Decimal("800"),
            )
        )

        application = await application_repo.get_by_id(result.application_id)
        assert result.status == ProjectApplicationStatus.APPLIED
        assert application.project_id == "project-1"
        assert application.freelancer_profile_id == "profile-1"
        assert application.submitted_by_user_id == "freelancer-1"
        assert uow.committed is True

    async def test_project_not_accepting_applications_raises(
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
        authorization_service.grant("freelancer-1", "project.apply")
        await make_project(project_id="project-1", status=ProjectStatus.ASSIGNED)
        await make_level(level_id="level-1")
        await make_profile(profile_id="profile-1", user_id="freelancer-1")
        use_case = build_apply(
            authorization_service, project_repo, application_repo, profile_repo, level_repo, id_generator, clock, uow
        )

        with pytest.raises(FreelancerNotEligibleError):
            await use_case.execute(ApplyForProjectCommand(actor_id="freelancer-1", project_id="project-1"))

    async def test_unapproved_freelancer_raises(
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
        authorization_service.grant("freelancer-1", "project.apply")
        await make_project(project_id="project-1", status=ProjectStatus.COLLECTING_APPLICATIONS)
        await make_level(level_id="level-1")
        await make_profile(
            profile_id="profile-1",
            user_id="freelancer-1",
            approval_status=FreelancerApprovalStatus.PENDING,
        )
        use_case = build_apply(
            authorization_service, project_repo, application_repo, profile_repo, level_repo, id_generator, clock, uow
        )

        with pytest.raises(FreelancerNotApprovedError):
            await use_case.execute(ApplyForProjectCommand(actor_id="freelancer-1", project_id="project-1"))

    async def test_duplicate_application_raises(
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
        authorization_service.grant("freelancer-1", "project.apply")
        await make_project(project_id="project-1", status=ProjectStatus.COLLECTING_APPLICATIONS)
        await make_level(level_id="level-1")
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
        use_case = build_apply(
            authorization_service, project_repo, application_repo, profile_repo, level_repo, id_generator, clock, uow
        )

        with pytest.raises(DuplicateApplicationError):
            await use_case.execute(ApplyForProjectCommand(actor_id="freelancer-1", project_id="project-1"))

    async def test_ineligible_due_to_active_count(
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
        authorization_service.grant("freelancer-1", "project.apply")
        await make_project(project_id="project-1", status=ProjectStatus.COLLECTING_APPLICATIONS)
        await make_level(level_id="level-1", max_active_applications=1)
        await make_profile(profile_id="profile-1", user_id="freelancer-1")
        now = await clock.now()
        await application_repo.add(
            ProjectApplication(
                id="app-0",
                project_id="other-project",
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
        use_case = build_apply(
            authorization_service, project_repo, application_repo, profile_repo, level_repo, id_generator, clock, uow
        )

        with pytest.raises(FreelancerNotEligibleError):
            await use_case.execute(ApplyForProjectCommand(actor_id="freelancer-1", project_id="project-1"))

    async def test_application_deadline_passed_raises(
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
        authorization_service.grant("freelancer-1", "project.apply")
        await make_project(
            project_id="project-1",
            status=ProjectStatus.COLLECTING_APPLICATIONS,
            application_deadline=datetime(2026, 7, 1, tzinfo=UTC),
        )
        await make_level(level_id="level-1")
        await make_profile(profile_id="profile-1", user_id="freelancer-1")
        use_case = build_apply(
            authorization_service, project_repo, application_repo, profile_repo, level_repo, id_generator, clock, uow
        )

        with pytest.raises(ApplicationDeadlineExpiredError):
            await use_case.execute(ApplyForProjectCommand(actor_id="freelancer-1", project_id="project-1"))

    async def test_apply_uses_submitted_by_actor(
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
        authorization_service.grant("admin-1", "project.apply")
        await make_project(project_id="project-1", status=ProjectStatus.COLLECTING_APPLICATIONS)
        await make_level(level_id="level-1")
        await make_profile(profile_id="profile-1", user_id="admin-1")
        use_case = build_apply(
            authorization_service, project_repo, application_repo, profile_repo, level_repo, id_generator, clock, uow
        )

        result = await use_case.execute(ApplyForProjectCommand(actor_id="admin-1", project_id="project-1"))

        application = await application_repo.get_by_id(result.application_id)
        assert application.submitted_by_user_id == "admin-1"


class TestWithdrawApplicationUseCase:
    async def test_withdraw_succeeds(self, application_repo, profile_repo, clock, uow, make_profile):
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
        use_case = WithdrawApplicationUseCase(
            application_repo=application_repo,
            profile_repo=profile_repo,
            clock=clock,
            uow=uow,
        )

        result = await use_case.execute(WithdrawApplicationCommand(actor_id="freelancer-1", application_id="app-1"))

        assert result.status == ProjectApplicationStatus.WITHDRAWN
        assert (await application_repo.get_by_id("app-1")).withdrawn_at == await clock.now()

    async def test_non_owner_raises(self, application_repo, profile_repo, clock, uow, make_profile):
        await make_profile(profile_id="profile-1", user_id="freelancer-1")
        now = await clock.now()
        await application_repo.add(
            ProjectApplication(
                id="app-1",
                project_id="project-1",
                freelancer_profile_id="profile-2",
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
        use_case = WithdrawApplicationUseCase(
            application_repo=application_repo,
            profile_repo=profile_repo,
            clock=clock,
            uow=uow,
        )

        with pytest.raises(PermissionDeniedError):
            await use_case.execute(WithdrawApplicationCommand(actor_id="freelancer-1", application_id="app-1"))
