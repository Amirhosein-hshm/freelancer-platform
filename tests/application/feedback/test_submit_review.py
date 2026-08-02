import pytest

from app.application.feedback.dto import SubmitReviewCommand
from app.application.feedback.use_cases.submit_review import SubmitReviewUseCase
from app.application.shared.exceptions import PermissionDeniedError, ValidationError
from app.domain.feedback.exceptions import ProjectNotCompletedError
from app.domain.project.enums import DeliveryStatus, ProjectStatus, RevisionRequestStatus
from app.domain.review.enums import ReviewStatus


def build_review(
    project_repo,
    customer_review_repo,
    delivery_repo,
    revision_repo,
    status_history_repo,
    id_generator,
    clock,
    uow,
) -> SubmitReviewUseCase:
    return SubmitReviewUseCase(
        project_repo=project_repo,
        customer_review_repo=customer_review_repo,
        delivery_repo=delivery_repo,
        revision_repo=revision_repo,
        status_history_repo=status_history_repo,
        id_generator=id_generator,
        clock=clock,
        uow=uow,
    )


class TestSubmitReviewUseCase:
    def test_approve_completes_project(
        self,
        project_repo,
        customer_review_repo,
        delivery_repo,
        revision_repo,
        status_history_repo,
        id_generator,
        clock,
        uow,
        make_project,
        make_delivery,
    ):
        make_project(status=ProjectStatus.AWAITING_CUSTOMER_REVIEW)
        make_delivery()
        use_case = build_review(
            project_repo,
            customer_review_repo,
            delivery_repo,
            revision_repo,
            status_history_repo,
            id_generator,
            clock,
            uow,
        )

        result = use_case.execute(
            SubmitReviewCommand(
                actor_id="customer-1",
                project_id="project-1",
                decision=ReviewStatus.APPROVED,
                comment="Excellent",
            )
        )

        assert result.decision == ReviewStatus.APPROVED
        assert result.project_status == ProjectStatus.COMPLETED
        project = project_repo.get_by_id("project-1")
        assert project.completed_at == clock.now()
        assert project.is_locked() is True
        review = customer_review_repo.find_by_project("project-1")
        assert review is not None
        assert review.comment == "Excellent"
        assert uow.committed is True
        history = status_history_repo.list_by_project("project-1")
        assert history[-1].to_status == ProjectStatus.COMPLETED

    def test_reject_requests_revision(
        self,
        project_repo,
        customer_review_repo,
        delivery_repo,
        revision_repo,
        status_history_repo,
        id_generator,
        clock,
        uow,
        make_project,
        make_delivery,
    ):
        make_project(status=ProjectStatus.AWAITING_CUSTOMER_REVIEW)
        make_delivery()
        use_case = build_review(
            project_repo,
            customer_review_repo,
            delivery_repo,
            revision_repo,
            status_history_repo,
            id_generator,
            clock,
            uow,
        )

        result = use_case.execute(
            SubmitReviewCommand(
                actor_id="customer-1",
                project_id="project-1",
                decision=ReviewStatus.REJECTED,
                comment="Needs fixes",
            )
        )

        assert result.project_status == ProjectStatus.REVISION_REQUESTED
        assert delivery_repo.get_by_id("delivery-1").status == DeliveryStatus.REVISED
        revision = revision_repo.list_by_project("project-1")
        assert len(revision) == 1
        assert revision[0].status == RevisionRequestStatus.OPEN
        assert revision[0].reason == "Needs fixes"

    def test_wrong_project_status_raises(
        self,
        project_repo,
        customer_review_repo,
        delivery_repo,
        revision_repo,
        status_history_repo,
        id_generator,
        clock,
        uow,
        make_project,
        make_delivery,
    ):
        make_project(status=ProjectStatus.IN_PROGRESS)
        make_delivery()
        use_case = build_review(
            project_repo,
            customer_review_repo,
            delivery_repo,
            revision_repo,
            status_history_repo,
            id_generator,
            clock,
            uow,
        )

        with pytest.raises(ProjectNotCompletedError):
            use_case.execute(
                SubmitReviewCommand(
                    actor_id="customer-1",
                    project_id="project-1",
                    decision=ReviewStatus.APPROVED,
                )
            )

    def test_non_owner_raises(
        self,
        project_repo,
        customer_review_repo,
        delivery_repo,
        revision_repo,
        status_history_repo,
        id_generator,
        clock,
        uow,
        make_project,
        make_delivery,
    ):
        make_project(status=ProjectStatus.AWAITING_CUSTOMER_REVIEW)
        make_delivery()
        use_case = build_review(
            project_repo,
            customer_review_repo,
            delivery_repo,
            revision_repo,
            status_history_repo,
            id_generator,
            clock,
            uow,
        )

        with pytest.raises(PermissionDeniedError):
            use_case.execute(
                SubmitReviewCommand(
                    actor_id="intruder",
                    project_id="project-1",
                    decision=ReviewStatus.APPROVED,
                )
            )

    def test_pending_decision_raises(
        self,
        project_repo,
        customer_review_repo,
        delivery_repo,
        revision_repo,
        status_history_repo,
        id_generator,
        clock,
        uow,
        make_project,
        make_delivery,
    ):
        make_project(status=ProjectStatus.AWAITING_CUSTOMER_REVIEW)
        make_delivery()
        use_case = build_review(
            project_repo,
            customer_review_repo,
            delivery_repo,
            revision_repo,
            status_history_repo,
            id_generator,
            clock,
            uow,
        )

        with pytest.raises(ValidationError):
            use_case.execute(
                SubmitReviewCommand(
                    actor_id="customer-1",
                    project_id="project-1",
                    decision=ReviewStatus.PENDING,
                )
            )
