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
    DuplicateApplicationError,
    FreelancerNotEligibleError,
)


def build_apply(
    project_repo, application_repo, profile_repo, level_repo, id_generator, clock, uow
) -> ApplyForProjectUseCase:
    return ApplyForProjectUseCase(
        project_repo=project_repo,
        application_repo=application_repo,
        profile_repo=profile_repo,
        level_repo=level_repo,
        id_generator=id_generator,
        clock=clock,
        uow=uow,
    )


def seed_application(
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
    return application_repo.add(ProjectApplication(**fields))  # type: ignore[arg-type]


class TestApplyForProjectUseCase:
    def test_apply_succeeds(
        self,
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
        make_project(project_id="project-1", status=ProjectStatus.COLLECTING_APPLICATIONS)
        make_level(level_id="level-1", max_active_applications=3)
        make_profile(profile_id="profile-1", user_id="freelancer-1")
        use_case = build_apply(
            project_repo, application_repo, profile_repo, level_repo, id_generator, clock, uow
        )

        result = use_case.execute(
            ApplyForProjectCommand(
                actor_id="freelancer-1",
                project_id="project-1",
                proposed_amount=Decimal("800"),
            )
        )

        application = application_repo.get_by_id(result.application_id)
        assert result.status == ProjectApplicationStatus.APPLIED
        assert application.project_id == "project-1"
        assert application.freelancer_profile_id == "profile-1"
        assert uow.committed is True

    def test_project_not_accepting_applications_raises(
        self,
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
        make_project(project_id="project-1", status=ProjectStatus.ASSIGNED)
        make_level(level_id="level-1")
        make_profile(profile_id="profile-1", user_id="freelancer-1")
        use_case = build_apply(
            project_repo, application_repo, profile_repo, level_repo, id_generator, clock, uow
        )

        with pytest.raises(FreelancerNotEligibleError):
            use_case.execute(ApplyForProjectCommand(actor_id="freelancer-1", project_id="project-1"))

    def test_unapproved_freelancer_raises(
        self,
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
        make_project(project_id="project-1", status=ProjectStatus.COLLECTING_APPLICATIONS)
        make_level(level_id="level-1")
        make_profile(
            profile_id="profile-1",
            user_id="freelancer-1",
            approval_status=FreelancerApprovalStatus.PENDING,
        )
        use_case = build_apply(
            project_repo, application_repo, profile_repo, level_repo, id_generator, clock, uow
        )

        with pytest.raises(FreelancerNotApprovedError):
            use_case.execute(ApplyForProjectCommand(actor_id="freelancer-1", project_id="project-1"))

    def test_duplicate_application_raises(
        self,
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
        make_project(project_id="project-1", status=ProjectStatus.COLLECTING_APPLICATIONS)
        make_level(level_id="level-1")
        make_profile(profile_id="profile-1", user_id="freelancer-1")
        application_repo.add(
            ProjectApplication(
                id="app-1",
                project_id="project-1",
                freelancer_profile_id="profile-1",
                status=ProjectApplicationStatus.APPLIED,
                cover_letter=None,
                proposed_amount=None,
                proposed_days=None,
                applied_at=clock.now(),
                decided_by_user_id=None,
                decided_at=None,
                decision_note=None,
                withdrawn_at=None,
                created_at=clock.now(),
            )
        )
        use_case = build_apply(
            project_repo, application_repo, profile_repo, level_repo, id_generator, clock, uow
        )

        with pytest.raises(DuplicateApplicationError):
            use_case.execute(ApplyForProjectCommand(actor_id="freelancer-1", project_id="project-1"))

    def test_ineligible_due_to_active_count(
        self,
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
        make_project(project_id="project-1", status=ProjectStatus.COLLECTING_APPLICATIONS)
        make_level(level_id="level-1", max_active_applications=1)
        make_profile(profile_id="profile-1", user_id="freelancer-1")
        application_repo.add(
            ProjectApplication(
                id="app-0",
                project_id="other-project",
                freelancer_profile_id="profile-1",
                status=ProjectApplicationStatus.APPLIED,
                cover_letter=None,
                proposed_amount=None,
                proposed_days=None,
                applied_at=clock.now(),
                decided_by_user_id=None,
                decided_at=None,
                decision_note=None,
                withdrawn_at=None,
                created_at=clock.now(),
            )
        )
        use_case = build_apply(
            project_repo, application_repo, profile_repo, level_repo, id_generator, clock, uow
        )

        with pytest.raises(FreelancerNotEligibleError):
            use_case.execute(ApplyForProjectCommand(actor_id="freelancer-1", project_id="project-1"))


class TestWithdrawApplicationUseCase:
    def test_withdraw_succeeds(self, application_repo, profile_repo, clock, uow, make_profile):
        make_profile(profile_id="profile-1", user_id="freelancer-1")
        application_repo.add(
            ProjectApplication(
                id="app-1",
                project_id="project-1",
                freelancer_profile_id="profile-1",
                status=ProjectApplicationStatus.APPLIED,
                cover_letter=None,
                proposed_amount=None,
                proposed_days=None,
                applied_at=clock.now(),
                decided_by_user_id=None,
                decided_at=None,
                decision_note=None,
                withdrawn_at=None,
                created_at=clock.now(),
            )
        )
        use_case = WithdrawApplicationUseCase(
            application_repo=application_repo,
            profile_repo=profile_repo,
            clock=clock,
            uow=uow,
        )

        result = use_case.execute(
            WithdrawApplicationCommand(actor_id="freelancer-1", application_id="app-1")
        )

        assert result.status == ProjectApplicationStatus.WITHDRAWN
        assert application_repo.get_by_id("app-1").withdrawn_at == clock.now()

    def test_non_owner_raises(self, application_repo, profile_repo, clock, uow, make_profile):
        make_profile(profile_id="profile-1", user_id="freelancer-1")
        application_repo.add(
            ProjectApplication(
                id="app-1",
                project_id="project-1",
                freelancer_profile_id="profile-2",
                status=ProjectApplicationStatus.APPLIED,
                cover_letter=None,
                proposed_amount=None,
                proposed_days=None,
                applied_at=clock.now(),
                decided_by_user_id=None,
                decided_at=None,
                decision_note=None,
                withdrawn_at=None,
                created_at=clock.now(),
            )
        )
        use_case = WithdrawApplicationUseCase(
            application_repo=application_repo,
            profile_repo=profile_repo,
            clock=clock,
            uow=uow,
        )

        with pytest.raises(PermissionDeniedError):
            use_case.execute(
                WithdrawApplicationCommand(actor_id="freelancer-1", application_id="app-1")
            )
