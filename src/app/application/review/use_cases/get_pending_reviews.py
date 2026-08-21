from app.application.review.dto import GetPendingReviewsQuery, GetPendingReviewsResult
from app.application.review.mapping import to_review_result
from app.application.shared.pagination import limit_offset
from app.application.shared.use_case import UseCase
from app.domain.review.repositories import ISupervisorReviewRepository


class GetPendingReviewsUseCase(UseCase[GetPendingReviewsQuery, GetPendingReviewsResult]):
    def __init__(self, review_repo: ISupervisorReviewRepository) -> None:
        self._review_repo = review_repo

    async def execute(self, request: GetPendingReviewsQuery) -> GetPendingReviewsResult:
        limit, offset = limit_offset(request.page, request.page_size)
        reviews = await self._review_repo.list_pending_for_supervisor(
            request.supervisor_user_id,
            limit=limit,
            offset=offset,
        )
        total_items = await self._review_repo.count_pending_for_supervisor(request.supervisor_user_id)
        return GetPendingReviewsResult(
            reviews=[to_review_result(r) for r in reviews],
            total_items=total_items,
            page=request.page,
            page_size=request.page_size,
        )