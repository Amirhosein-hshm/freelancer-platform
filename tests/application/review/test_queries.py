from app.application.review.dto import (
    GetPendingReviewsQuery,
    GetSupervisorProjectsQuery,
)
from app.application.review.use_cases.get_pending_reviews import GetPendingReviewsUseCase
from app.application.review.use_cases.get_supervisor_projects import GetSupervisorProjectsUseCase
from app.domain.review.enums import ReviewStatus


class TestGetSupervisorProjectsUseCase:
    def test_lists_projects_assigned_to_supervisor(self, project_repo, seed_supervisor_flow):
        seed_supervisor_flow(project_id="project-1")
        seed_supervisor_flow(project_id="project-2", supervisor_user_id="supervisor-2")
        use_case = GetSupervisorProjectsUseCase(project_repo=project_repo)

        result = use_case.execute(GetSupervisorProjectsQuery(supervisor_user_id="supervisor-1"))

        assert [p.project_id for p in result.projects] == ["project-1"]


class TestGetPendingReviewsUseCase:
    def test_lists_only_pending_reviews_of_supervisor(self, review_repo, seed_supervisor_flow, clock):
        seed_supervisor_flow(delivery_id="delivery-1")
        seed_supervisor_flow(delivery_id="delivery-2", supervisor_user_id="supervisor-2")
        seed_supervisor_flow(delivery_id="delivery-3", project_id="project-3", category_id="cat-2")
        decided = review_repo.get_by_delivery("delivery-3")
        decided.approve("Done", clock.now())
        review_repo.update(decided)
        use_case = GetPendingReviewsUseCase(review_repo=review_repo)

        result = use_case.execute(GetPendingReviewsQuery(supervisor_user_id="supervisor-1"))

        assert [r.project_delivery_id for r in result.reviews] == ["delivery-1"]
        assert result.reviews[0].decision == ReviewStatus.PENDING
