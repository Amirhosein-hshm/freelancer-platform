from decimal import Decimal

import pytest

from app.application.project.dto import (
    AcceptFreelancerCommand,
    RejectFreelancerCommand,
    ViewApplicationsQuery,
)
from app.application.project.use_cases.accept_freelancer import AcceptFreelancerUseCase
from app.application.project.use_cases.reject_freelancer import RejectFreelancerUseCase
from app.application.project.use_cases.view_applications import ViewApplicationsUseCase
from app.application.shared.exceptions import PermissionDeniedError
from app.domain.project.entities import ProjectApplication
from app.domain.project.enums import ProjectApplicationStatus, ProjectStatus


def add_application(
    application_repo,
    app_id: str,
    profile_id: str,
    status: ProjectApplicationStatus = ProjectApplicationStatus.APPLIED,
    now=None,
) -> ProjectApplication:
    application = ProjectApplication(
        id=app_id,
        project_id="project-1",
        freelancer_profile_id=profile_id,
        status=status,
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


class TestAcceptFreelancerUseCase:
    def test_accept_selection_and_rejects_others(
        self, project_repo, application_repo, status_history_repo, id_generator, clock, uow, make_project
    ):
        make_project(
            project_id="project-1",
            customer_user_id="customer-1",
            status=ProjectStatus.COLLECTING_APPLICATIONS,
        )
        add_application(application_repo, "app-1", "profile-1", now=clock.now())
        add_application(application_repo, "app-2", "profile-2", now=clock.now())
        use_case = AcceptFreelancerUseCase(
            project_repo=project_repo,
            application_repo=application_repo,
            status_history_repo=status_history_repo,
            id_generator=id_generator,
            clock=clock,
            uow=uow,
        )

        result = use_case.execute(AcceptFreelancerCommand(actor_id="customer-1", application_id="app-1"))

        assert result.selected_application_id == "app-1"
        assert result.status == ProjectStatus.ASSIGNED
        project = project_repo.get_by_id("project-1")
        assert project.selected_application_id == "app-1"
        assert application_repo.get_by_id("app-1").status == ProjectApplicationStatus.ACCEPTED
        assert application_repo.get_by_id("app-2").status == ProjectApplicationStatus.REJECTED
        assert len(status_history_repo.list_by_project("project-1")) == 1

    def test_non_owner_raises(
        self, project_repo, application_repo, status_history_repo, id_generator, clock, uow, make_project
    ):
        make_project(project_id="project-1", customer_user_id="customer-1")
        add_application(application_repo, "app-1", "profile-1", now=clock.now())
        use_case = AcceptFreelancerUseCase(
            project_repo=project_repo,
            application_repo=application_repo,
            status_history_repo=status_history_repo,
            id_generator=id_generator,
            clock=clock,
            uow=uow,
        )

        with pytest.raises(PermissionDeniedError):
            use_case.execute(AcceptFreelancerCommand(actor_id="intruder", application_id="app-1"))


class TestRejectFreelancerUseCase:
    def test_reject_application(self, project_repo, application_repo, clock, uow, make_project):
        make_project(project_id="project-1", customer_user_id="customer-1")
        add_application(application_repo, "app-1", "profile-1", now=clock.now())
        use_case = RejectFreelancerUseCase(
            project_repo=project_repo, application_repo=application_repo, clock=clock, uow=uow
        )

        result = use_case.execute(
            RejectFreelancerCommand(actor_id="customer-1", application_id="app-1", note="No fit")
        )

        assert result.status == ProjectApplicationStatus.REJECTED
        assert application_repo.get_by_id("app-1").decision_note == "No fit"

    def test_non_owner_raises(self, project_repo, application_repo, clock, uow, make_project):
        make_project(project_id="project-1", customer_user_id="customer-1")
        add_application(application_repo, "app-1", "profile-1", now=clock.now())
        use_case = RejectFreelancerUseCase(
            project_repo=project_repo, application_repo=application_repo, clock=clock, uow=uow
        )

        with pytest.raises(PermissionDeniedError):
            use_case.execute(
                RejectFreelancerCommand(actor_id="intruder", application_id="app-1")
            )


class TestViewApplicationsUseCase:
    def test_view_applications_as_customer(self, project_repo, application_repo, clock, make_project):
        make_project(project_id="project-1", customer_user_id="customer-1")
        add_application(application_repo, "app-1", "profile-1", now=clock.now())
        add_application(application_repo, "app-2", "profile-2", now=clock.now())
        use_case = ViewApplicationsUseCase(
            project_repo=project_repo, application_repo=application_repo
        )

        result = use_case.execute(ViewApplicationsQuery(actor_id="customer-1", project_id="project-1"))

        assert len(result.applications) == 2

    def test_non_owner_raises(self, project_repo, application_repo, make_project):
        make_project(project_id="project-1", customer_user_id="customer-1")
        use_case = ViewApplicationsUseCase(
            project_repo=project_repo, application_repo=application_repo
        )

        with pytest.raises(PermissionDeniedError):
            use_case.execute(ViewApplicationsQuery(actor_id="intruder", project_id="project-1"))
