import pytest

from app.application.feedback.dto import DeleteRatingCommand, UpdateRatingCommand
from app.application.feedback.use_cases.delete_rating import DeleteRatingUseCase
from app.application.feedback.use_cases.update_rating import UpdateRatingUseCase
from app.domain.feedback.exceptions import InvalidRatingScoreError, RatingNotFoundError
from app.domain.project.enums import ProjectStatus


class TestUpdateRatingUseCase:
    async def test_update_rating_succeeds(
        self,
        authorization_service,
        project_repo,
        rating_repo,
        uow,
        make_project,
        make_customer_review,
        make_rating,
    ):
        await make_project(status=ProjectStatus.COMPLETED)
        await make_customer_review()
        await make_rating()
        authorization_service.grant("customer-1", "feedback.manage_own")
        use_case = UpdateRatingUseCase(project_repo, rating_repo, authorization_service, uow)

        await use_case.execute(
            UpdateRatingCommand(
                actor_id="customer-1",
                rating_id="rating-1",
                score=3,
                comment="ok",
                is_public=True,
            )
        )

        rating = await rating_repo.get_by_id("rating-1")
        assert rating.score == 3
        assert rating.comment == "ok"
        assert rating.is_public is True
        assert uow.committed is True

    async def test_invalid_score_raises(
        self,
        authorization_service,
        project_repo,
        rating_repo,
        uow,
        make_project,
        make_customer_review,
        make_rating,
    ):
        await make_project(status=ProjectStatus.COMPLETED)
        await make_customer_review()
        await make_rating()
        authorization_service.grant("customer-1", "feedback.manage_own")
        use_case = UpdateRatingUseCase(project_repo, rating_repo, authorization_service, uow)

        with pytest.raises(InvalidRatingScoreError):
            await use_case.execute(UpdateRatingCommand(actor_id="customer-1", rating_id="rating-1", score=0))


class TestDeleteRatingUseCase:
    async def test_delete_rating_succeeds(
        self,
        authorization_service,
        project_repo,
        rating_repo,
        uow,
        make_project,
        make_customer_review,
        make_rating,
    ):
        await make_project(status=ProjectStatus.COMPLETED)
        await make_customer_review()
        await make_rating()
        authorization_service.grant("customer-1", "feedback.manage_own")
        use_case = DeleteRatingUseCase(project_repo, rating_repo, authorization_service, uow)

        await use_case.execute(DeleteRatingCommand(actor_id="customer-1", rating_id="rating-1"))

        with pytest.raises(RatingNotFoundError):
            await rating_repo.get_by_id("rating-1")
        assert uow.committed is True
