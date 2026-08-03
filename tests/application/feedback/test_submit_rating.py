import pytest

from app.application.feedback.dto import SubmitRatingCommand
from app.application.feedback.use_cases.submit_rating import SubmitRatingUseCase
from app.application.shared.exceptions import PermissionDeniedError, ValidationError
from app.domain.feedback.exceptions import (
    InvalidRatingScoreError,
    ProjectNotCompletedError,
    RatingAlreadyExistsError,
)
from app.domain.project.enums import ProjectStatus


def build_rating(
    authorization_service,
    project_repo,
    application_repo,
    customer_review_repo,
    rating_repo,
    id_generator,
    clock,
    uow,
) -> SubmitRatingUseCase:
    return SubmitRatingUseCase(
        authorization_service=authorization_service,
        project_repo=project_repo,
        application_repo=application_repo,
        customer_review_repo=customer_review_repo,
        rating_repo=rating_repo,
        id_generator=id_generator,
        clock=clock,
        uow=uow,
    )


class TestSubmitRatingUseCase:
    def test_submit_rating_succeeds(
        self,
        authorization_service,
        project_repo,
        application_repo,
        customer_review_repo,
        rating_repo,
        id_generator,
        clock,
        uow,
        make_project,
        make_application,
        make_customer_review,
    ):
        make_project(status=ProjectStatus.COMPLETED)
        make_application()
        make_customer_review()
        authorization_service.grant("customer-1", "feedback.manage_own")
        use_case = build_rating(
            authorization_service,
            project_repo,
            application_repo,
            customer_review_repo,
            rating_repo,
            id_generator,
            clock,
            uow,
        )

        use_case.execute(
            SubmitRatingCommand(
                actor_id="customer-1", project_id="project-1", score=5, is_public=True
            )
        )

        rating = rating_repo.find_by_project("project-1")
        assert rating is not None
        assert rating.score == 5
        assert rating.is_public is True
        assert rating.freelancer_profile_id == "profile-1"
        assert uow.committed is True

    def test_not_completed_raises(
        self,
        authorization_service,
        project_repo,
        application_repo,
        customer_review_repo,
        rating_repo,
        id_generator,
        clock,
        uow,
        make_project,
    ):
        make_project(status=ProjectStatus.IN_PROGRESS)
        authorization_service.grant("customer-1", "feedback.manage_own")
        use_case = build_rating(
            authorization_service,
            project_repo,
            application_repo,
            customer_review_repo,
            rating_repo,
            id_generator,
            clock,
            uow,
        )

        with pytest.raises(ProjectNotCompletedError):
            use_case.execute(
                SubmitRatingCommand(actor_id="customer-1", project_id="project-1", score=4)
            )

    def test_duplicate_rating_raises(
        self,
        authorization_service,
        project_repo,
        application_repo,
        customer_review_repo,
        rating_repo,
        id_generator,
        clock,
        uow,
        make_project,
        make_application,
        make_customer_review,
        make_rating,
    ):
        make_project(status=ProjectStatus.COMPLETED)
        make_application()
        make_customer_review()
        make_rating()
        authorization_service.grant("customer-1", "feedback.manage_own")
        use_case = build_rating(
            authorization_service,
            project_repo,
            application_repo,
            customer_review_repo,
            rating_repo,
            id_generator,
            clock,
            uow,
        )

        with pytest.raises(RatingAlreadyExistsError):
            use_case.execute(
                SubmitRatingCommand(actor_id="customer-1", project_id="project-1", score=3)
            )

    def test_invalid_score_raises(
        self,
        authorization_service,
        project_repo,
        application_repo,
        customer_review_repo,
        rating_repo,
        id_generator,
        clock,
        uow,
        make_project,
        make_application,
        make_customer_review,
    ):
        make_project(status=ProjectStatus.COMPLETED)
        make_application()
        make_customer_review()
        authorization_service.grant("customer-1", "feedback.manage_own")
        use_case = build_rating(
            authorization_service,
            project_repo,
            application_repo,
            customer_review_repo,
            rating_repo,
            id_generator,
            clock,
            uow,
        )

        with pytest.raises(InvalidRatingScoreError):
            use_case.execute(
                SubmitRatingCommand(actor_id="customer-1", project_id="project-1", score=9)
            )

    def test_missing_customer_review_raises(
        self,
        authorization_service,
        project_repo,
        application_repo,
        customer_review_repo,
        rating_repo,
        id_generator,
        clock,
        uow,
        make_project,
        make_application,
    ):
        make_project(status=ProjectStatus.COMPLETED)
        make_application()
        authorization_service.grant("customer-1", "feedback.manage_own")
        use_case = build_rating(
            authorization_service,
            project_repo,
            application_repo,
            customer_review_repo,
            rating_repo,
            id_generator,
            clock,
            uow,
        )

        with pytest.raises(ValidationError):
            use_case.execute(
                SubmitRatingCommand(actor_id="customer-1", project_id="project-1", score=4)
            )

    def test_non_owner_raises(
        self,
        authorization_service,
        project_repo,
        application_repo,
        customer_review_repo,
        rating_repo,
        id_generator,
        clock,
        uow,
        make_project,
        make_application,
        make_customer_review,
    ):
        make_project(status=ProjectStatus.COMPLETED)
        make_application()
        make_customer_review()
        use_case = build_rating(
            authorization_service,
            project_repo,
            application_repo,
            customer_review_repo,
            rating_repo,
            id_generator,
            clock,
            uow,
        )

        with pytest.raises(PermissionDeniedError):
            use_case.execute(
                SubmitRatingCommand(actor_id="intruder", project_id="project-1", score=4)
            )
