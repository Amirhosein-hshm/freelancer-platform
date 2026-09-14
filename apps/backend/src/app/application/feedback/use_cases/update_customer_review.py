from app.application.feedback.dto import (
    UpdateCustomerReviewCommand,
    UpdateCustomerReviewResult,
)
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
from app.domain.feedback.repositories import ICustomerReviewRepository
from app.domain.project.repositories import IProjectRepository


class UpdateCustomerReviewUseCase(UseCase[UpdateCustomerReviewCommand, UpdateCustomerReviewResult]):
    def __init__(
        self,
        project_repo: IProjectRepository,
        customer_review_repo: ICustomerReviewRepository,
        authorization_service: IAuthorizationService,
        uow: IUnitOfWork,
    ) -> None:
        self._project_repo = project_repo
        self._customer_review_repo = customer_review_repo
        self._authorization_service = authorization_service
        self._uow = uow

    async def execute(self, request: UpdateCustomerReviewCommand) -> UpdateCustomerReviewResult:
        review = await self._customer_review_repo.get_by_id(request.review_id)
        project = await self._project_repo.get_by_id(review.project_id)
        await authorize_owned_action(
            self._authorization_service,
            request.actor_id,
            project.customer_user_id,
            PERMISSION_FEEDBACK_MANAGE_OWN,
            PERMISSION_FEEDBACK_MANAGE_ANY,
        )
        review.update_comment(request.comment)
        async with self._uow:
            await self._customer_review_repo.update(review)
            await self._uow.commit()
        return UpdateCustomerReviewResult(review_id=review.id)
