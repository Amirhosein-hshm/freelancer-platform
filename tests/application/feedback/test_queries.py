from decimal import Decimal

from app.application.feedback.dto import (
    GetFreelancerRatingsQuery,
    GetProjectRatingQuery,
)
from app.application.feedback.use_cases.get_freelancer_ratings import (
    GetFreelancerRatingsUseCase,
)
from app.application.feedback.use_cases.get_project_rating import GetProjectRatingUseCase


class TestGetFreelancerRatingsUseCase:
    def test_lists_ratings_and_average(self, rating_repo, make_rating):
        make_rating(rating_id="rating-1", score=5)
        make_rating(rating_id="rating-2", score=4, project_id="project-2")
        make_rating(rating_id="rating-3", score=3, project_id="project-3", freelancer_profile_id="profile-2")
        use_case = GetFreelancerRatingsUseCase(rating_repo=rating_repo)

        result = use_case.execute(GetFreelancerRatingsQuery(freelancer_profile_id="profile-1"))

        assert [r.rating_id for r in result.ratings] == ["rating-1", "rating-2"]
        assert result.average_score == Decimal("4.5")

    def test_empty_has_no_average(self, rating_repo):
        use_case = GetFreelancerRatingsUseCase(rating_repo=rating_repo)

        result = use_case.execute(GetFreelancerRatingsQuery(freelancer_profile_id="profile-1"))

        assert result.ratings == []
        assert result.average_score is None


class TestGetProjectRatingUseCase:
    def test_returns_rating_for_project(self, rating_repo, make_rating):
        make_rating()
        use_case = GetProjectRatingUseCase(rating_repo=rating_repo)

        result = use_case.execute(GetProjectRatingQuery(project_id="project-1"))

        assert result.rating is not None
        assert result.rating.score == 5

    def test_missing_rating_returns_none(self, rating_repo):
        use_case = GetProjectRatingUseCase(rating_repo=rating_repo)

        result = use_case.execute(GetProjectRatingQuery(project_id="project-1"))

        assert result.rating is None
