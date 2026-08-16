from app.application.project.permissions import (
    PERMISSION_PROJECT_MANAGE_ANY,
    PERMISSION_PROJECT_MANAGE_OWN,
)
from app.application.review.dto import (
    GetSupervisorReviewQuery,
    GetSupervisorReviewResult,
    ReviewResult,
)
from app.application.review.use_cases.review_workflow import (
    PERMISSION_REVIEW_DECIDE_OWN,
)
from app.application.shared.authorization import (
    IAuthorizationService,
    authorize_owned_action,
)
from app.application.shared.use_case import UseCase
from app.domain.category.repositories import ICategorySupervisorRepository
from app.domain.project.repositories import IProjectDeliveryRepository, IProjectRepository
from app.domain.review.repositories import ISupervisorReviewRepository


class GetSupervisorReviewUseCase(UseCase[GetSupervisorReviewQuery, GetSupervisorReviewResult]):
    def __init__(
        self,
        project_repo: IProjectRepository,
        delivery_repo: IProjectDeliveryRepository,
        review_repo: ISupervisorReviewRepository,
        category_supervisor_repo: ICategorySupervisorRepository,
        authorization_service: IAuthorizationService,
    ) -> None:
        self._project_repo = project_repo
        self._delivery_repo = delivery_repo
        self._review_repo = review_repo
        self._category_supervisor_repo = category_supervisor_repo
        self._authorization_service = authorization_service

    async def execute(self, request: GetSupervisorReviewQuery) -> GetSupervisorReviewResult:
        delivery = await self._delivery_repo.get_by_id(request.project_delivery_id)
        project = await self._project_repo.get_by_id(delivery.project_id)
        review = await self._review_repo.get_by_delivery(request.project_delivery_id)

        is_supervisor = await self._category_supervisor_repo.is_supervisor_of(request.actor_id, project.category_id)
        if is_supervisor:
            await self._authorization_service.require_permission(request.actor_id, PERMISSION_REVIEW_DECIDE_OWN)
        else:
            await authorize_owned_action(
                self._authorization_service,
                request.actor_id,
                project.customer_user_id,
                PERMISSION_PROJECT_MANAGE_OWN,
                PERMISSION_PROJECT_MANAGE_ANY,
            )

        return GetSupervisorReviewResult(
            review=ReviewResult(
                review_id=review.id,
                project_delivery_id=review.project_delivery_id,
                project_id=review.project_id,
                supervisor_user_id=review.supervisor_user_id,
                decision=review.decision,
                reject_reason=review.reject_reason,
                notes=review.notes,
                reviewed_at=review.reviewed_at,
            )
        )
