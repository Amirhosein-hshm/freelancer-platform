from app.application.feedback.dto import GetProjectRatingQuery, GetProjectRatingResult
from app.application.feedback.mapping import to_rating_result
from app.application.shared.use_case import UseCase
from app.domain.feedback.repositories import IRatingRepository


class GetProjectRatingUseCase(UseCase[GetProjectRatingQuery, GetProjectRatingResult]):
    def __init__(self, rating_repo: IRatingRepository) -> None:
        self._rating_repo = rating_repo

    async def execute(self, request: GetProjectRatingQuery) -> GetProjectRatingResult:
        rating = await self._rating_repo.find_by_project(request.project_id)
        return GetProjectRatingResult(
            rating=to_rating_result(rating) if rating is not None else None
        )
