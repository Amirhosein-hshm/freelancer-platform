from app.application.review.dto import GetPendingReviewsQuery, GetPendingReviewsResult
from app.application.review.mapping import to_review_result
from app.application.shared.use_case import UseCase
from app.domain.review.repositories import ISupervisorReviewRepository


class GetPendingReviewsUseCase(
    UseCase[GetPendingReviewsQuery, GetPendingReviewsResult]
):
    def __init__(self, review_repo: ISupervisorReviewRepository) -> None:
        self._review_repo = review_repo

    def execute(self, request: GetPendingReviewsQuery) -> GetPendingReviewsResult:
        reviews = self._review_repo.list_pending_for_supervisor(request.supervisor_user_id)
        return GetPendingReviewsResult(reviews=[to_review_result(r) for r in reviews])
