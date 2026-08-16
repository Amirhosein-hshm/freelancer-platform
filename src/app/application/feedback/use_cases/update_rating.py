from app.application.feedback.dto import UpdateRatingCommand, UpdateRatingResult
from app.application.feedback.permissions import (
    PERMISSION_FEEDBACK_MANAGE_ANY,
    PERMISSION_FEEDBACK_MANAGE_OWN,
)
from app.application.shared.authorization import (
    IAuthorizationService,
    authorize_owned_action,
)
from app.application.shared.ports import IUnitOfWork
from app.application.shared.use_case import UseCase
from app.domain.feedback.repositories import IRatingRepository
from app.domain.project.repositories import IProjectRepository


class UpdateRatingUseCase(UseCase[UpdateRatingCommand, UpdateRatingResult]):
    def __init__(
        self,
        project_repo: IProjectRepository,
        rating_repo: IRatingRepository,
        authorization_service: IAuthorizationService,
        uow: IUnitOfWork,
    ) -> None:
        self._project_repo = project_repo
        self._rating_repo = rating_repo
        self._authorization_service = authorization_service
        self._uow = uow

    async def execute(self, request: UpdateRatingCommand) -> UpdateRatingResult:
        rating = await self._rating_repo.get_by_id(request.rating_id)
        project = await self._project_repo.get_by_id(rating.project_id)
        await authorize_owned_action(
            self._authorization_service,
            request.actor_id,
            project.customer_user_id,
            PERMISSION_FEEDBACK_MANAGE_OWN,
            PERMISSION_FEEDBACK_MANAGE_ANY,
        )
        rating.update_details(request.score, request.comment, request.is_public)
        async with self._uow:
            await self._rating_repo.update(rating)
            await self._uow.commit()
        return UpdateRatingResult(rating_id=rating.id)
