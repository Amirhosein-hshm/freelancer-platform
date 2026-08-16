import pytest

from app.application.review.dto import RejectDeliveryCommand
from app.application.review.use_cases.reject_delivery import RejectDeliveryUseCase
from app.application.shared.exceptions import PermissionDeniedError
from app.domain.project.enums import DeliveryStatus, ProjectStatus, RevisionRequestStatus
from app.domain.review.enums import ReviewStatus


def build_reject(
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
) -> RejectDeliveryUseCase:
    return RejectDeliveryUseCase(
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


class TestRejectDeliveryUseCase:
    async def test_reject_triggers_revision_request(
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
        use_case = build_reject(
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
            RejectDeliveryCommand(actor_id="supervisor-1", project_delivery_id="delivery-1", reason="Buggy")
        )

        assert result.decision == ReviewStatus.REJECTED
        assert result.project_status == ProjectStatus.REVISION_REQUESTED
        assert (await delivery_repo.get_by_id("delivery-1")).status == DeliveryStatus.REJECTED
        assert (await review_repo.get_by_delivery("delivery-1")).reject_reason == "Buggy"
        revision = await revision_repo.list_by_project("project-1")
        assert len(revision) == 1
        assert revision[0].status == RevisionRequestStatus.OPEN
        assert revision[0].reason == "Buggy"
        assert revision[0].round_no == 1
        assert uow.committed is True

    async def test_non_supervisor_raises(
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
        use_case = build_reject(
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

        with pytest.raises(PermissionDeniedError):
            await use_case.execute(
                RejectDeliveryCommand(actor_id="intruder", project_delivery_id="delivery-1", reason="Nope")
            )
