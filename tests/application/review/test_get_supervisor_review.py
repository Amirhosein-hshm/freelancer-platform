import pytest

from app.application.review.dto import GetSupervisorReviewQuery
from app.application.review.use_cases.get_supervisor_review import GetSupervisorReviewUseCase
from app.application.shared.exceptions import PermissionDeniedError


class TestGetSupervisorReviewUseCase:
    async def test_supervisor_can_read_review(
        self,
        authorization_service,
        project_repo,
        delivery_repo,
        review_repo,
        category_supervisor_repo,
        seed_supervisor_flow,
    ):
        await seed_supervisor_flow()
        authorization_service.grant("supervisor-1", "review.decide_own")
        use_case = GetSupervisorReviewUseCase(
            project_repo, delivery_repo, review_repo, category_supervisor_repo, authorization_service
        )

        result = await use_case.execute(
            GetSupervisorReviewQuery(actor_id="supervisor-1", project_delivery_id="delivery-1")
        )

        assert result.review.project_delivery_id == "delivery-1"

    async def test_project_owner_can_read_review(
        self,
        authorization_service,
        project_repo,
        delivery_repo,
        review_repo,
        category_supervisor_repo,
        seed_supervisor_flow,
    ):
        await seed_supervisor_flow()
        authorization_service.grant("customer-1", "project.manage_own")
        use_case = GetSupervisorReviewUseCase(
            project_repo, delivery_repo, review_repo, category_supervisor_repo, authorization_service
        )

        result = await use_case.execute(
            GetSupervisorReviewQuery(actor_id="customer-1", project_delivery_id="delivery-1")
        )

        assert result.review.project_delivery_id == "delivery-1"

    async def test_unauthorized_user_raises(
        self,
        authorization_service,
        project_repo,
        delivery_repo,
        review_repo,
        category_supervisor_repo,
        seed_supervisor_flow,
    ):
        await seed_supervisor_flow()
        use_case = GetSupervisorReviewUseCase(
            project_repo, delivery_repo, review_repo, category_supervisor_repo, authorization_service
        )

        with pytest.raises(PermissionDeniedError):
            await use_case.execute(GetSupervisorReviewQuery(actor_id="intruder", project_delivery_id="delivery-1"))
