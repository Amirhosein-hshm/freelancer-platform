from app.application.feedback.dto import (
    GetFreelancerRatingsQuery,
    GetFreelancerRatingsResult,
)
from app.application.feedback.mapping import to_rating_result
from app.application.shared.use_case import UseCase
from app.domain.feedback.repositories import IRatingRepository


class GetFreelancerRatingsUseCase(UseCase[GetFreelancerRatingsQuery, GetFreelancerRatingsResult]):
    def __init__(self, rating_repo: IRatingRepository) -> None:
        self._rating_repo = rating_repo

    async def execute(self, request: GetFreelancerRatingsQuery) -> GetFreelancerRatingsResult:
        ratings = await self._rating_repo.list_by_freelancer(request.freelancer_profile_id)
        average = await self._rating_repo.average_score_for_freelancer(request.freelancer_profile_id)
        return GetFreelancerRatingsResult(
            ratings=[to_rating_result(r) for r in ratings],
            average_score=average,
        )
