from decimal import Decimal

import pytest

from app.application.project.dto import (
    CompleteProjectCommand,
    RequestRevisionCommand,
    SubmitDeliveryCommand,
)
from app.application.project.use_cases.complete_project import CompleteProjectUseCase
from app.application.project.use_cases.request_revision import RequestRevisionUseCase
from app.application.project.use_cases.submit_delivery import SubmitDeliveryUseCase
from app.application.shared.exceptions import PermissionDeniedError
from app.domain.project.entities import ProjectApplication, ProjectDelivery, ProjectRevisionRequest
from app.domain.project.enums import (
    DeliveryStatus,
    ProjectApplicationStatus,
    ProjectStatus,
    RevisionRequestStatus,
)
from app.domain.project.exceptions import MaxRevisionsExceededError
from app.domain.review.enums import ReviewStatus


def add_application(application_repo, app_id: str = "app-1", now=None) -> ProjectApplication:
    application = ProjectApplication(
        id=app_id,
        project_id="project-1",
        freelancer_profile_id="profile-1",
        status=ProjectApplicationStatus.ACCEPTED,
        cover_letter=None,
        proposed_amount=Decimal("800"),
        proposed_days=10,
        applied_at=now,
        decided_by_user_id="customer-1",
        decided_at=now,
        decision_note=None,
        withdrawn_at=None,
        created_at=now,
    )
    application_repo.add(application)
    return application


def add_delivery(
    delivery_repo,
    delivery_id: str = "delivery-1",
    version_no: int = 1,
    status: DeliveryStatus = DeliveryStatus.SUBMITTED,
    now=None,
) -> ProjectDelivery:
    delivery = ProjectDelivery(
        id=delivery_id,
        project_id="project-1",
        version_no=version_no,
        submitted_by_user_id="freelancer-1",
        status=status,
        delivery_note=None,
        submitted_at=now,
        reviewed_at=None,
        reviewer_user_id=None,
        superseded_by_delivery_id=None,
        file_asset_ids=[],
        created_at=now,
    )
    delivery_repo.add(delivery)
    return delivery


def build_submit(
    project_repo,
    application_repo,
    delivery_repo,
    status_history_repo,
    profile_repo,
    review_repo,
    id_generator,
    clock,
    uow,
) -> SubmitDeliveryUseCase:
    return SubmitDeliveryUseCase(
        project_repo=project_repo,
        application_repo=application_repo,
        delivery_repo=delivery_repo,
        status_history_repo=status_history_repo,
        profile_repo=profile_repo,
        review_repo=review_repo,
        id_generator=id_generator,
        clock=clock,
        uow=uow,
    )


class TestSubmitDeliveryUseCase:
    def test_first_delivery_moves_to_supervisor_review(
        self,
        project_repo,
        application_repo,
        delivery_repo,
        status_history_repo,
        profile_repo,
        review_repo,
        id_generator,
        clock,
        uow,
        make_project,
        make_profile,
    ):
        make_project(project_id="project-1", status=ProjectStatus.IN_PROGRESS, selected_application_id="app-1")
        make_profile(profile_id="profile-1", user_id="freelancer-1")
        add_application(application_repo, now=clock.now())
        use_case = build_submit(
            project_repo,
            application_repo,
            delivery_repo,
            status_history_repo,
            profile_repo,
            review_repo,
            id_generator,
            clock,
            uow,
        )

        result = use_case.execute(
            SubmitDeliveryCommand(actor_id="freelancer-1", project_id="project-1", delivery_note="v1")
        )

        assert result.version_no == 1
        assert result.project_status == ProjectStatus.UNDER_SUPERVISOR_REVIEW
        assert delivery_repo.get_by_id(result.delivery_id).status == DeliveryStatus.UNDER_REVIEW
        review = review_repo.find_by_delivery(result.delivery_id)
        assert review is not None
        assert review.supervisor_user_id == "supervisor-1"
        assert review.decision == ReviewStatus.PENDING
        assert uow.committed is True

    def test_delivery_without_supervisor_goes_to_customer(
        self,
        project_repo,
        application_repo,
        delivery_repo,
        status_history_repo,
        profile_repo,
        review_repo,
        id_generator,
        clock,
        uow,
        make_project,
        make_profile,
    ):
        make_project(
            project_id="project-1",
            status=ProjectStatus.IN_PROGRESS,
            selected_application_id="app-1",
            assigned_supervisor_user_id=None,
        )
        make_profile(profile_id="profile-1", user_id="freelancer-1")
        add_application(application_repo, now=clock.now())
        use_case = build_submit(
            project_repo,
            application_repo,
            delivery_repo,
            status_history_repo,
            profile_repo,
            review_repo,
            id_generator,
            clock,
            uow,
        )

        result = use_case.execute(
            SubmitDeliveryCommand(actor_id="freelancer-1", project_id="project-1")
        )

        assert result.project_status == ProjectStatus.AWAITING_CUSTOMER_REVIEW
        assert delivery_repo.get_by_id(result.delivery_id).status == DeliveryStatus.SUBMITTED

    def test_second_delivery_after_revision_supersedes_previous(
        self,
        project_repo,
        application_repo,
        delivery_repo,
        status_history_repo,
        profile_repo,
        review_repo,
        id_generator,
        clock,
        uow,
        make_project,
        make_profile,
    ):
        make_project(project_id="project-1", status=ProjectStatus.REVISION_REQUESTED, selected_application_id="app-1")
        make_profile(profile_id="profile-1", user_id="freelancer-1")
        add_application(application_repo, now=clock.now())
        add_delivery(delivery_repo, now=clock.now(), status=DeliveryStatus.REVISED)
        use_case = build_submit(
            project_repo,
            application_repo,
            delivery_repo,
            status_history_repo,
            profile_repo,
            review_repo,
            id_generator,
            clock,
            uow,
        )

        result = use_case.execute(
            SubmitDeliveryCommand(actor_id="freelancer-1", project_id="project-1")
        )

        assert result.version_no == 2
        assert result.project_status == ProjectStatus.UNDER_SUPERVISOR_REVIEW
        old = delivery_repo.get_by_id("delivery-1")
        assert old.status == DeliveryStatus.SUPERSEDED
        assert old.superseded_by_delivery_id == result.delivery_id

    def test_non_selected_freelancer_raises(
        self,
        project_repo,
        application_repo,
        delivery_repo,
        status_history_repo,
        profile_repo,
        review_repo,
        id_generator,
        clock,
        uow,
        make_project,
        make_profile,
    ):
        make_project(project_id="project-1", status=ProjectStatus.IN_PROGRESS, selected_application_id="app-1")
        make_profile(profile_id="profile-1", user_id="freelancer-1")
        add_application(application_repo, now=clock.now())
        use_case = build_submit(
            project_repo,
            application_repo,
            delivery_repo,
            status_history_repo,
            profile_repo,
            review_repo,
            id_generator,
            clock,
            uow,
        )

        with pytest.raises(PermissionDeniedError):
            use_case.execute(
                SubmitDeliveryCommand(actor_id="other-user", project_id="project-1")
            )


def build_revision(
    project_repo, revision_repo, delivery_repo, status_history_repo, id_generator, clock, uow
) -> RequestRevisionUseCase:
    return RequestRevisionUseCase(
        project_repo=project_repo,
        revision_repo=revision_repo,
        delivery_repo=delivery_repo,
        status_history_repo=status_history_repo,
        id_generator=id_generator,
        clock=clock,
        uow=uow,
    )


class TestRequestRevisionUseCase:
    def test_request_revision_opens_request_and_marks_delivery_revised(
        self, project_repo, revision_repo, delivery_repo, status_history_repo, id_generator, clock, uow, make_project
    ):
        make_project(project_id="project-1", status=ProjectStatus.AWAITING_CUSTOMER_REVIEW)
        add_delivery(delivery_repo, now=clock.now(), status=DeliveryStatus.UNDER_REVIEW)
        use_case = build_revision(
            project_repo, revision_repo, delivery_repo, status_history_repo, id_generator, clock, uow
        )

        result = use_case.execute(
            RequestRevisionCommand(actor_id="customer-1", project_id="project-1", reason="Fix auth")
        )

        assert result.round_no == 1
        assert result.project_status == ProjectStatus.REVISION_REQUESTED
        revision = revision_repo.list_by_project("project-1")[0]
        assert revision.status == RevisionRequestStatus.OPEN
        assert revision.project_delivery_id == "delivery-1"
        assert delivery_repo.get_by_id("delivery-1").status == DeliveryStatus.REVISED

    def test_max_revisions_exceeded_raises(
        self, project_repo, revision_repo, delivery_repo, status_history_repo, id_generator, clock, uow, make_project
    ):
        make_project(project_id="project-1", status=ProjectStatus.AWAITING_CUSTOMER_REVIEW)
        for i in range(3):
            revision_repo.add(
                ProjectRevisionRequest(
                    id=f"rev-{i}",
                    project_id="project-1",
                    project_delivery_id=None,
                    requested_by_user_id="customer-1",
                    requested_to_user_id=None,
                    round_no=i + 1,
                    status=RevisionRequestStatus.CLOSED,
                    reason="x",
                    resolved_by_user_id=None,
                    requested_at=clock.now(),
                    resolved_at=None,
                    created_at=clock.now(),
                )
            )
        use_case = build_revision(
            project_repo, revision_repo, delivery_repo, status_history_repo, id_generator, clock, uow
        )

        with pytest.raises(MaxRevisionsExceededError):
            use_case.execute(
                RequestRevisionCommand(actor_id="customer-1", project_id="project-1", reason="again")
            )


def build_complete(project_repo, status_history_repo, id_generator, clock, uow) -> CompleteProjectUseCase:
    return CompleteProjectUseCase(
        project_repo=project_repo,
        status_history_repo=status_history_repo,
        id_generator=id_generator,
        clock=clock,
        uow=uow,
    )


class TestCompleteProjectUseCase:
    def test_complete_awaited_project(self, project_repo, status_history_repo, id_generator, clock, uow, make_project):
        make_project(project_id="project-1", status=ProjectStatus.AWAITING_CUSTOMER_REVIEW)
        use_case = build_complete(project_repo, status_history_repo, id_generator, clock, uow)

        result = use_case.execute(
            CompleteProjectCommand(actor_id="customer-1", project_id="project-1")
        )

        assert result.status == ProjectStatus.COMPLETED
        assert project_repo.get_by_id("project-1").completed_at == clock.now()

    def test_complete_wrong_status_raises(
        self, project_repo, status_history_repo, id_generator, clock, uow, make_project
    ):
        make_project(project_id="project-1", status=ProjectStatus.IN_PROGRESS)
        use_case = build_complete(project_repo, status_history_repo, id_generator, clock, uow)

        with pytest.raises(PermissionDeniedError):
            use_case.execute(
                CompleteProjectCommand(actor_id="customer-1", project_id="project-1")
            )
