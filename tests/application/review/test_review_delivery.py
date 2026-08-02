import pytest

from app.application.review.dto import ReviewDeliveryCommand
from app.application.review.use_cases.review_delivery import ReviewDeliveryUseCase
from app.application.shared.exceptions import ValidationError
from app.domain.project.enums import ProjectStatus
from app.domain.review.enums import ReviewStatus


def build_review(
    delivery_repo,
    project_repo,
    category_supervisor_repo,
    review_repo,
    revision_repo,
    status_history_repo,
    id_generator,
    clock,
    uow,
) -> ReviewDeliveryUseCase:
    return ReviewDeliveryUseCase(
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


class TestReviewDeliveryUseCase:
    def test_review_approves(
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
        use_case = build_review(
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
            ReviewDeliveryCommand(
                actor_id="supervisor-1",
                project_delivery_id="delivery-1",
                decision=ReviewStatus.APPROVED,
                notes="Good",
            )
        )

        assert result.project_status == ProjectStatus.AWAITING_CUSTOMER_REVIEW
        assert review_repo.get_by_delivery("delivery-1").decision == ReviewStatus.APPROVED

    def test_review_rejects(
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
        use_case = build_review(
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
            ReviewDeliveryCommand(
                actor_id="supervisor-1",
                project_delivery_id="delivery-1",
                decision=ReviewStatus.REJECTED,
                reject_reason="Fixes required",
            )
        )

        assert result.project_status == ProjectStatus.REVISION_REQUESTED
        assert review_repo.get_by_delivery("delivery-1").decision == ReviewStatus.REJECTED

    def test_pending_decision_is_rejected(
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
        use_case = build_review(
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

        with pytest.raises(ValidationError):
            use_case.execute(
                ReviewDeliveryCommand(
                    actor_id="supervisor-1",
                    project_delivery_id="delivery-1",
                    decision=ReviewStatus.PENDING,
                )
            )
