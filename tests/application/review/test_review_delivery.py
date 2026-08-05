import pytest

from app.application.review.dto import ReviewDeliveryCommand
from app.application.review.use_cases.review_delivery import ReviewDeliveryUseCase
from app.application.shared.exceptions import ValidationError
from app.domain.project.enums import ProjectStatus
from app.domain.review.enums import ReviewStatus
from app.domain.shared.exceptions import InvalidStateTransitionError


def build_review(
    authorization_service,
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
        authorization_service=authorization_service,
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
    async def test_review_approves(
        self,
        authorization_service,
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
        await seed_supervisor_flow()
        authorization_service.grant("supervisor-1", "review.decide_own")
        use_case = build_review(
            authorization_service,
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

        result = await use_case.execute(
            ReviewDeliveryCommand(
                actor_id="supervisor-1",
                project_delivery_id="delivery-1",
                decision=ReviewStatus.APPROVED,
                notes="Good",
            )
        )

        assert result.project_status == ProjectStatus.AWAITING_CUSTOMER_REVIEW
        assert (await review_repo.get_by_delivery("delivery-1")).decision == ReviewStatus.APPROVED

    async def test_review_rejects(
        self,
        authorization_service,
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
        await seed_supervisor_flow()
        authorization_service.grant("supervisor-1", "review.decide_own")
        use_case = build_review(
            authorization_service,
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

        result = await use_case.execute(
            ReviewDeliveryCommand(
                actor_id="supervisor-1",
                project_delivery_id="delivery-1",
                decision=ReviewStatus.REJECTED,
                reject_reason="Fixes required",
            )
        )

        assert result.project_status == ProjectStatus.REVISION_REQUESTED
        assert (await review_repo.get_by_delivery("delivery-1")).decision == ReviewStatus.REJECTED

    async def test_pending_decision_is_rejected(
        self,
        authorization_service,
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
        await seed_supervisor_flow()
        authorization_service.grant("supervisor-1", "review.decide_own")
        use_case = build_review(
            authorization_service,
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
            await use_case.execute(
                ReviewDeliveryCommand(
                    actor_id="supervisor-1",
                    project_delivery_id="delivery-1",
                    decision=ReviewStatus.PENDING,
                )
            )

    async def test_review_requires_project_under_supervisor_review(
        self,
        authorization_service,
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
        await seed_supervisor_flow()
        project = await project_repo.get_by_id("project-1")
        project.status = ProjectStatus.AWAITING_CUSTOMER_REVIEW
        await project_repo.update(project)
        authorization_service.grant("supervisor-1", "review.decide_own")
        use_case = build_review(
            authorization_service,
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

        with pytest.raises(InvalidStateTransitionError):
            await use_case.execute(
                ReviewDeliveryCommand(
                    actor_id="supervisor-1",
                    project_delivery_id="delivery-1",
                    decision=ReviewStatus.APPROVED,
                )
            )
