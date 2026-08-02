import pytest

from app.application.review.dto import ApproveDeliveryCommand
from app.application.review.use_cases.approve_delivery import ApproveDeliveryUseCase
from app.domain.project.enums import DeliveryStatus, ProjectStatus
from app.domain.review.enums import ReviewStatus
from app.domain.review.exceptions import (
    DeliveryAlreadyReviewedError,
    NotAssignedSupervisorError,
)


def build_approve(
    delivery_repo,
    project_repo,
    category_supervisor_repo,
    review_repo,
    revision_repo,
    status_history_repo,
    id_generator,
    clock,
    uow,
) -> ApproveDeliveryUseCase:
    return ApproveDeliveryUseCase(
        delivery_repo=delivery_repo,
        project_repo=project_repo,
        category_supervisor_repo=category_supervisor_repo,
        review_repo=review_repo,
        revision_repo=revision_repo,
        status_history_repo=status_history_repo,
        id_generator=id_generator,
        clock=clock,
        uow=uow,
    )


class TestApproveDeliveryUseCase:
    def test_approve_moves_project_to_customer_review(
        self,
        delivery_repo,
        project_repo,
        category_supervisor_repo,
        review_repo,
        revision_repo,
        status_history_repo,
        id_generator,
        clock,
        uow,
        seed_supervisor_flow,
    ):
        seed_supervisor_flow()
        use_case = build_approve(
            delivery_repo,
            project_repo,
            category_supervisor_repo,
            review_repo,
            revision_repo,
            status_history_repo,
            id_generator,
            clock,
            uow,
        )

        result = use_case.execute(
            ApproveDeliveryCommand(
                actor_id="supervisor-1", project_delivery_id="delivery-1", notes="OK"
            )
        )

        assert result.decision == ReviewStatus.APPROVED
        assert result.project_status == ProjectStatus.AWAITING_CUSTOMER_REVIEW
        assert delivery_repo.get_by_id("delivery-1").status == DeliveryStatus.APPROVED
        review = review_repo.get_by_delivery("delivery-1")
        assert review.decision == ReviewStatus.APPROVED
        assert review.notes == "OK"
        assert uow.committed is True
        history = status_history_repo.list_by_project("project-1")
        assert history[-1].to_status == ProjectStatus.AWAITING_CUSTOMER_REVIEW

    def test_non_supervisor_raises(
        self,
        delivery_repo,
        project_repo,
        category_supervisor_repo,
        review_repo,
        revision_repo,
        status_history_repo,
        id_generator,
        clock,
        uow,
        seed_supervisor_flow,
    ):
        seed_supervisor_flow()
        use_case = build_approve(
            delivery_repo,
            project_repo,
            category_supervisor_repo,
            review_repo,
            revision_repo,
            status_history_repo,
            id_generator,
            clock,
            uow,
        )

        with pytest.raises(NotAssignedSupervisorError):
            use_case.execute(
                ApproveDeliveryCommand(
                    actor_id="intruder", project_delivery_id="delivery-1"
                )
            )

    def test_already_reviewed_raises(
        self,
        delivery_repo,
        project_repo,
        category_supervisor_repo,
        review_repo,
        revision_repo,
        status_history_repo,
        id_generator,
        clock,
        uow,
        seed_supervisor_flow,
    ):
        seed_supervisor_flow()
        use_case = build_approve(
            delivery_repo,
            project_repo,
            category_supervisor_repo,
            review_repo,
            revision_repo,
            status_history_repo,
            id_generator,
            clock,
            uow,
        )
        use_case.execute(
            ApproveDeliveryCommand(actor_id="supervisor-1", project_delivery_id="delivery-1")
        )

        with pytest.raises(DeliveryAlreadyReviewedError):
            use_case.execute(
                ApproveDeliveryCommand(actor_id="supervisor-1", project_delivery_id="delivery-1")
            )

    def test_missing_pending_review_creates_one(
        self,
        delivery_repo,
        project_repo,
        category_supervisor_repo,
        review_repo,
        revision_repo,
        status_history_repo,
        id_generator,
        clock,
        uow,
        seed_supervisor_flow,
    ):
        seed_supervisor_flow(with_review=False)
        use_case = build_approve(
            delivery_repo,
            project_repo,
            category_supervisor_repo,
            review_repo,
            revision_repo,
            status_history_repo,
            id_generator,
            clock,
            uow,
        )

        result = use_case.execute(
            ApproveDeliveryCommand(actor_id="supervisor-1", project_delivery_id="delivery-1")
        )

        assert review_repo.get_by_delivery("delivery-1").decision == ReviewStatus.APPROVED
        assert result.project_status == ProjectStatus.AWAITING_CUSTOMER_REVIEW
