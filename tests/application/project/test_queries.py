from decimal import Decimal

import pytest

from app.application.project.dto import (
    GetAvailableProjectsQuery,
    GetMyProjectsQuery,
    GetProjectDetailsQuery,
    ListVisibleProjectsQuery,
)
from app.application.project.use_cases.get_available_projects import GetAvailableProjectsUseCase
from app.application.project.use_cases.get_my_projects import GetMyProjectsUseCase
from app.application.project.use_cases.get_project_details import GetProjectDetailsUseCase
from app.application.project.use_cases.list_visible_projects import ListVisibleProjectsUseCase
from app.domain.freelancer.enums import FreelancerApprovalStatus
from app.domain.freelancer.exceptions import FreelancerNotApprovedError
from app.domain.project.entities import ProjectApplication, ProjectDelivery
from app.domain.project.enums import (
    DeliveryStatus,
    ProjectApplicationStatus,
    ProjectStatus,
)
from app.domain.project.value_objects import ProjectCode
from tests.fakes.fake_authorization_service import FakeAuthorizationService
from tests.fakes.fake_freelancer_profile_repository import FakeFreelancerProfileRepository


async def add_application(application_repo, app_id: str, now) -> ProjectApplication:
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
    await application_repo.add(application)
    return application


class TestGetProjectDetailsUseCase:
    async def test_details_include_applications_and_deliveries(
        self, project_repo, application_repo, delivery_repo, category_supervisor_repo, clock, make_project
    ):
        await make_project(project_id="project-1", status=ProjectStatus.IN_PROGRESS)
        await add_application(application_repo, "app-1", await clock.now())
        now = await clock.now()
        await delivery_repo.add(
            ProjectDelivery(
                id="delivery-1",
                project_id="project-1",
                version_no=1,
                submitted_by_user_id="freelancer-1",
                status=DeliveryStatus.SUBMITTED,
                delivery_note=None,
                submitted_at=now,
                reviewed_at=None,
                reviewer_user_id=None,
                superseded_by_delivery_id=None,
                file_asset_ids=[],
                created_at=now,
            )
        )
        use_case = GetProjectDetailsUseCase(
            project_repo=project_repo,
            application_repo=application_repo,
            delivery_repo=delivery_repo,
            authorization_service=FakeAuthorizationService(),
            profile_repo=FakeFreelancerProfileRepository(),
            category_supervisor_repo=category_supervisor_repo,
        )

        result = await use_case.execute(GetProjectDetailsQuery(project_id="project-1"))

        assert result.project.project_id == "project-1"
        assert result.project.project_code == "PRJ-2026-001"
        assert len(result.applications) == 1
        assert len(result.deliveries) == 1


class TestGetMyProjectsUseCase:
    async def test_lists_projects_for_customer(self, project_repo, make_project):
        await make_project(project_id="project-1", customer_user_id="customer-1")
        await make_project(
            project_id="project-2",
            customer_user_id="customer-1",
            project_code=ProjectCode("PRJ-2026-002"),
        )
        await make_project(
            project_id="project-3",
            customer_user_id="other-customer",
            project_code=ProjectCode("PRJ-2026-003"),
        )
        use_case = GetMyProjectsUseCase(project_repo=project_repo)

        result = await use_case.execute(GetMyProjectsQuery(customer_user_id="customer-1"))

        assert [p.project_id for p in result.projects] == ["project-1", "project-2"]


class TestGetAvailableProjectsUseCase:
    async def test_returns_open_projects_for_approved_freelancer(
        self, project_repo, profile_repo, level_repo, make_project, make_profile, make_level
    ):
        await make_level(level_id="level-1")
        await make_profile(profile_id="profile-1", user_id="freelancer-1")
        await make_project(project_id="project-1", status=ProjectStatus.COLLECTING_APPLICATIONS)
        await make_project(
            project_id="project-2",
            status=ProjectStatus.IN_PROGRESS,
            project_code=ProjectCode("PRJ-2026-002"),
        )
        use_case = GetAvailableProjectsUseCase(
            project_repo=project_repo, profile_repo=profile_repo, level_repo=level_repo
        )

        result = await use_case.execute(GetAvailableProjectsQuery(actor_id="freelancer-1"))

        assert [p.project_id for p in result.projects] == ["project-1"]

    async def test_unapproved_freelancer_raises(self, project_repo, profile_repo, level_repo, make_profile):
        await make_profile(
            profile_id="profile-1",
            user_id="freelancer-1",
            approval_status=FreelancerApprovalStatus.PENDING,
        )
        use_case = GetAvailableProjectsUseCase(
            project_repo=project_repo, profile_repo=profile_repo, level_repo=level_repo
        )

        with pytest.raises(FreelancerNotApprovedError):
            await use_case.execute(GetAvailableProjectsQuery(actor_id="freelancer-1"))


class TestListVisibleProjectsUseCase:
    async def test_admin_sees_all_projects_without_freelancer_profile(
        self, project_repo, authorization_service, make_project
    ):
        await make_project(project_id="project-1", customer_user_id="customer-1")
        await make_project(
            project_id="project-2",
            customer_user_id="customer-2",
            project_code=ProjectCode("PRJ-2026-002"),
        )
        authorization_service.grant("admin-1", "project.manage_any")
        use_case = ListVisibleProjectsUseCase(project_repo, authorization_service)

        result = await use_case.execute(ListVisibleProjectsQuery(actor_id="admin-1"))

        assert {project.project_id for project in result.projects} == {"project-1", "project-2"}

    async def test_customer_and_supervisor_see_only_related_projects(
        self, project_repo, authorization_service, make_project
    ):
        await make_project(project_id="owned", customer_user_id="user-1", assigned_supervisor_user_id=None)
        await make_project(
            project_id="supervised",
            customer_user_id="customer-2",
            assigned_supervisor_user_id="user-1",
            project_code=ProjectCode("PRJ-2026-002"),
        )
        await make_project(
            project_id="unrelated",
            customer_user_id="customer-3",
            assigned_supervisor_user_id=None,
            project_code=ProjectCode("PRJ-2026-003"),
        )
        authorization_service.assign_role("user-1", "customer")
        authorization_service.assign_role("user-1", "supervisor")
        use_case = ListVisibleProjectsUseCase(project_repo, authorization_service)

        result = await use_case.execute(ListVisibleProjectsQuery(actor_id="user-1"))

        assert {project.project_id for project in result.projects} == {"owned", "supervised"}
