from app.application.review.dto import ReviewDeliveryCommand, ReviewDeliveryResult
from app.application.review.use_cases.review_workflow import decide_delivery_review
from app.application.shared.authorization import IAuthorizationService
from app.application.shared.ports import IClock, IIdGenerator, IUnitOfWork
from app.application.shared.use_case import UseCase
from app.domain.category.repositories import ICategorySupervisorRepository
from app.domain.project.repositories import (
    IProjectDeliveryRepository,
    IProjectRepository,
    IProjectRevisionRequestRepository,
    IProjectStatusHistoryRepository,
)
from app.domain.review.repositories import ISupervisorReviewRepository


class ReviewDeliveryUseCase(UseCase[ReviewDeliveryCommand, ReviewDeliveryResult]):
    def __init__(
        self,
        authorization_service: IAuthorizationService,
        delivery_repo: IProjectDeliveryRepository,
        project_repo: IProjectRepository,
        category_supervisor_repo: ICategorySupervisorRepository,
        review_repo: ISupervisorReviewRepository,
        revision_repo: IProjectRevisionRequestRepository,
        status_history_repo: IProjectStatusHistoryRepository,
        id_generator: IIdGenerator,
        clock: IClock,
        uow: IUnitOfWork,
    ) -> None:
        self._authorization_service = authorization_service
        self._delivery_repo = delivery_repo
        self._project_repo = project_repo
        self._category_supervisor_repo = category_supervisor_repo
        self._review_repo = review_repo
        self._revision_repo = revision_repo
        self._status_history_repo = status_history_repo
        self._id_generator = id_generator
        self._clock = clock
        self._uow = uow

    async def execute(self, request: ReviewDeliveryCommand) -> ReviewDeliveryResult:
        return await decide_delivery_review(
            authorization_service=self._authorization_service,
            delivery_repo=self._delivery_repo,
            project_repo=self._project_repo,
            category_supervisor_repo=self._category_supervisor_repo,
            review_repo=self._review_repo,
            revision_repo=self._revision_repo,
            status_history_repo=self._status_history_repo,
            id_generator=self._id_generator,
            clock=self._clock,
            uow=self._uow,
            actor_id=request.actor_id,
            delivery_id=request.project_delivery_id,
            decision=request.decision,
            notes=request.notes,
            reject_reason=request.reject_reason,
        )
