from decimal import Decimal

import pytest

from app.application.project.dto import (
    GetAvailableProjectsQuery,
    GetMyProjectsQuery,
    GetProjectDetailsQuery,
)
from app.application.project.use_cases.get_available_projects import GetAvailableProjectsUseCase
from app.application.project.use_cases.get_my_projects import GetMyProjectsUseCase
from app.application.project.use_cases.get_project_details import GetProjectDetailsUseCase
from app.domain.freelancer.enums import FreelancerApprovalStatus
from app.domain.freelancer.exceptions import FreelancerNotApprovedError
from app.domain.project.entities import ProjectApplication, ProjectDelivery
from app.domain.project.enums import (
    DeliveryStatus,
    ProjectApplicationStatus,
    ProjectStatus,
)
from app.domain.project.value_objects import ProjectCode


def add_application(application_repo, app_id: str, now) -> ProjectApplication:
    application = ProjectApplication(
        id=app_id,
        project_id="project-1",
        freelancer_profile_id="profile-1",
        status=ProjectApplicationStatus.APPLIED,
        cover_letter=None,
        proposed_amount=Decimal("800"),
        proposed_days=10,
        applied_at=now,
        decided_by_user_id=None,
        decided_at=None,
        decision_note=None,
        withdrawn_at=None,
        created_at=now,
    )
    application_repo.add(application)
    return application


class TestGetProjectDetailsUseCase:
    def test_details_include_applications_and_deliveries(
        self, project_repo, application_repo, delivery_repo, clock, make_project
    ):
        make_project(project_id="project-1", status=ProjectStatus.IN_PROGRESS)
        add_application(application_repo, "app-1", clock.now())
        delivery_repo.add(
            ProjectDelivery(
                id="delivery-1",
                project_id="project-1",
                version_no=1,
                submitted_by_user_id="freelancer-1",
                status=DeliveryStatus.SUBMITTED,
                delivery_note=None,
                submitted_at=clock.now(),
                reviewed_at=None,
                reviewer_user_id=None,
                superseded_by_delivery_id=None,
                file_asset_ids=[],
                created_at=clock.now(),
            )
        )
        use_case = GetProjectDetailsUseCase(
            project_repo=project_repo,
            application_repo=application_repo,
            delivery_repo=delivery_repo,
        )

        result = use_case.execute(GetProjectDetailsQuery(project_id="project-1"))

        assert result.project.project_id == "project-1"
        assert result.project.project_code == "PRJ-2026-001"
        assert len(result.applications) == 1
        assert len(result.deliveries) == 1


class TestGetMyProjectsUseCase:
    def test_lists_projects_for_customer(self, project_repo, make_project):
        make_project(project_id="project-1", customer_user_id="customer-1")
        make_project(
            project_id="project-2",
            customer_user_id="customer-1",
            project_code=ProjectCode("PRJ-2026-002"),
        )
        make_project(
            project_id="project-3",
            customer_user_id="other-customer",
            project_code=ProjectCode("PRJ-2026-003"),
        )
        use_case = GetMyProjectsUseCase(project_repo=project_repo)

        result = use_case.execute(GetMyProjectsQuery(customer_user_id="customer-1"))

        assert [p.project_id for p in result.projects] == ["project-1", "project-2"]


class TestGetAvailableProjectsUseCase:
    def test_returns_open_projects_for_approved_freelancer(
        self, project_repo, profile_repo, level_repo, make_project, make_profile, make_level
    ):
        make_level(level_id="level-1")
        make_profile(profile_id="profile-1", user_id="freelancer-1")
        make_project(project_id="project-1", status=ProjectStatus.COLLECTING_APPLICATIONS)
        make_project(
            project_id="project-2",
            status=ProjectStatus.IN_PROGRESS,
            project_code=ProjectCode("PRJ-2026-002"),
        )
        use_case = GetAvailableProjectsUseCase(
            project_repo=project_repo, profile_repo=profile_repo, level_repo=level_repo
        )

        result = use_case.execute(GetAvailableProjectsQuery(actor_id="freelancer-1"))

        assert [p.project_id for p in result.projects] == ["project-1"]

    def test_unapproved_freelancer_raises(self, project_repo, profile_repo, level_repo, make_profile):
        make_profile(
            profile_id="profile-1",
            user_id="freelancer-1",
            approval_status=FreelancerApprovalStatus.PENDING,
        )
        use_case = GetAvailableProjectsUseCase(
            project_repo=project_repo, profile_repo=profile_repo, level_repo=level_repo
        )

        with pytest.raises(FreelancerNotApprovedError):
            use_case.execute(GetAvailableProjectsQuery(actor_id="freelancer-1"))
