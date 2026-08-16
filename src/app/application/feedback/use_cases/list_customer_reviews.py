from app.application.feedback.dto import (
    ListCustomerReviewsQuery,
    ListCustomerReviewsResult,
)
from app.application.feedback.mapping import to_review_result
from app.application.feedback.permissions import (
    PERMISSION_FEEDBACK_MANAGE_ANY,
    PERMISSION_FEEDBACK_MANAGE_OWN,
)
from app.application.shared.authorization import (
    IAuthorizationService,
    authorize_owned_action,
)
from app.application.shared.use_case import UseCase
from app.domain.feedback.repositories import ICustomerReviewRepository
from app.domain.project.repositories import IProjectRepository


class ListCustomerReviewsUseCase(UseCase[ListCustomerReviewsQuery, ListCustomerReviewsResult]):
    def __init__(
        self,
        project_repo: IProjectRepository,
        customer_review_repo: ICustomerReviewRepository,
        authorization_service: IAuthorizationService,
    ) -> None:
        self._project_repo = project_repo
        self._customer_review_repo = customer_review_repo
        self._authorization_service = authorization_service

    async def execute(self, request: ListCustomerReviewsQuery) -> ListCustomerReviewsResult:
        project = await self._project_repo.get_by_id(request.project_id)
        await authorize_owned_action(
            self._authorization_service,
            request.actor_id,
            project.customer_user_id,
            PERMISSION_FEEDBACK_MANAGE_OWN,
            PERMISSION_FEEDBACK_MANAGE_ANY,
        )
        reviews = await self._customer_review_repo.list_by_project(project.id)
        return ListCustomerReviewsResult(
            project_id=project.id,
            reviews=[to_review_result(r) for r in reviews],
        )
