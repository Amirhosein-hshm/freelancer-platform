from app.application.review.dto import (
    GetPendingReviewsQuery,
    GetSupervisorProjectsQuery,
)
from app.application.review.use_cases.get_pending_reviews import GetPendingReviewsUseCase
from app.application.review.use_cases.get_supervisor_projects import GetSupervisorProjectsUseCase
from app.domain.review.enums import ReviewStatus


class TestGetSupervisorProjectsUseCase:
    async def test_lists_projects_assigned_to_supervisor(self, project_repo, seed_supervisor_flow):
        await seed_supervisor_flow(project_id="project-1")
        await seed_supervisor_flow(project_id="project-2", supervisor_user_id="supervisor-2")
        use_case = GetSupervisorProjectsUseCase(project_repo=project_repo)

        result = await use_case.execute(GetSupervisorProjectsQuery(supervisor_user_id="supervisor-1"))

        assert [p.project_id for p in result.projects] == ["project-1"]


class TestGetPendingReviewsUseCase:
    async def test_lists_only_pending_reviews_of_supervisor(self, review_repo, seed_supervisor_flow, clock):
        await seed_supervisor_flow(delivery_id="delivery-1")
        await seed_supervisor_flow(delivery_id="delivery-2", supervisor_user_id="supervisor-2")
        await seed_supervisor_flow(delivery_id="delivery-3", project_id="project-3", category_id="cat-2")
        decided = await review_repo.get_by_delivery("delivery-3")
        decided.approve("Done", await clock.now())
        await review_repo.update(decided)
        use_case = GetPendingReviewsUseCase(review_repo=review_repo)

        result = await use_case.execute(GetPendingReviewsQuery(supervisor_user_id="supervisor-1"))

        assert [r.project_delivery_id for r in result.reviews] == ["delivery-1"]
        assert result.reviews[0].decision == ReviewStatus.PENDING
