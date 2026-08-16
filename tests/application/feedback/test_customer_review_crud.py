from datetime import UTC, datetime

import pytest

from app.application.feedback.dto import (
    DeleteCustomerReviewCommand,
    GetCustomerReviewQuery,
    ListCustomerReviewsQuery,
    UpdateCustomerReviewCommand,
)
from app.application.feedback.use_cases.delete_customer_review import DeleteCustomerReviewUseCase
from app.application.feedback.use_cases.get_customer_review import GetCustomerReviewUseCase
from app.application.feedback.use_cases.list_customer_reviews import ListCustomerReviewsUseCase
from app.application.feedback.use_cases.update_customer_review import UpdateCustomerReviewUseCase
from app.application.shared.exceptions import PermissionDeniedError
from app.domain.feedback.exceptions import CustomerReviewNotFoundError
from app.domain.project.enums import ProjectStatus


class TestGetCustomerReviewUseCase:
    async def test_get_review_succeeds_for_owner(
        self,
        authorization_service,
        project_repo,
        customer_review_repo,
        make_project,
        make_customer_review,
    ):
        await make_project(status=ProjectStatus.COMPLETED)
        await make_customer_review()
        authorization_service.grant("customer-1", "feedback.manage_own")
        use_case = GetCustomerReviewUseCase(project_repo, customer_review_repo, authorization_service)

        result = await use_case.execute(GetCustomerReviewQuery(actor_id="customer-1", review_id="review-1"))

        assert result.review.review_id == "review-1"

    async def test_get_review_denied_for_non_owner(
        self,
        authorization_service,
        project_repo,
        customer_review_repo,
        make_project,
        make_customer_review,
    ):
        await make_project(status=ProjectStatus.COMPLETED)
        await make_customer_review()
        use_case = GetCustomerReviewUseCase(project_repo, customer_review_repo, authorization_service)

        with pytest.raises(PermissionDeniedError):
            await use_case.execute(GetCustomerReviewQuery(actor_id="intruder", review_id="review-1"))


class TestListCustomerReviewsUseCase:
    async def test_lists_reviews_ordered_by_reviewed_at_desc(
        self,
        authorization_service,
        project_repo,
        customer_review_repo,
        make_project,
        make_customer_review,
    ):
        await make_project(status=ProjectStatus.COMPLETED)
        await make_customer_review(review_id="review-1", reviewed_at=datetime(2026, 1, 1, tzinfo=UTC))
        await make_customer_review(review_id="review-2", reviewed_at=datetime(2026, 1, 2, tzinfo=UTC))
        authorization_service.grant("customer-1", "feedback.manage_own")
        use_case = ListCustomerReviewsUseCase(project_repo, customer_review_repo, authorization_service)

        result = await use_case.execute(ListCustomerReviewsQuery(actor_id="customer-1", project_id="project-1"))

        assert [r.review_id for r in result.reviews] == ["review-2", "review-1"]


class TestUpdateCustomerReviewUseCase:
    async def test_update_comment_succeeds(
        self,
        authorization_service,
        project_repo,
        customer_review_repo,
        uow,
        make_project,
        make_customer_review,
    ):
        await make_project(status=ProjectStatus.COMPLETED)
        await make_customer_review()
        authorization_service.grant("customer-1", "feedback.manage_own")
        use_case = UpdateCustomerReviewUseCase(project_repo, customer_review_repo, authorization_service, uow)

        await use_case.execute(
            UpdateCustomerReviewCommand(actor_id="customer-1", review_id="review-1", comment="updated")
        )

        review = await customer_review_repo.get_by_id("review-1")
        assert review.comment == "updated"
        assert uow.committed is True


class TestDeleteCustomerReviewUseCase:
    async def test_delete_succeeds(
        self,
        authorization_service,
        project_repo,
        customer_review_repo,
        uow,
        make_project,
        make_customer_review,
    ):
        await make_project(status=ProjectStatus.COMPLETED)
        await make_customer_review()
        authorization_service.grant("customer-1", "feedback.manage_own")
        use_case = DeleteCustomerReviewUseCase(project_repo, customer_review_repo, authorization_service, uow)

        await use_case.execute(DeleteCustomerReviewCommand(actor_id="customer-1", review_id="review-1"))

        with pytest.raises(CustomerReviewNotFoundError):
            await customer_review_repo.get_by_id("review-1")
        assert uow.committed is True
