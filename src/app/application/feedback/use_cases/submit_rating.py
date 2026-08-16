from app.application.feedback.dto import SubmitRatingCommand, SubmitRatingResult
from app.application.feedback.permissions import (
    PERMISSION_FEEDBACK_MANAGE_ANY,
    PERMISSION_FEEDBACK_MANAGE_OWN,
)
from app.application.shared.authorization import (
    IAuthorizationService,
    authorize_owned_action,
)
from app.application.shared.exceptions import ValidationError
from app.application.shared.ports import IClock, IIdGenerator, IUnitOfWork
from app.application.shared.use_case import UseCase
from app.domain.feedback.entities import Rating
from app.domain.feedback.exceptions import (
    CustomerReviewNotApprovedError,
    ProjectNotCompletedError,
    RatingAlreadyExistsError,
)
from app.domain.feedback.repositories import ICustomerReviewRepository, IRatingRepository
from app.domain.project.enums import ProjectStatus
from app.domain.project.repositories import (
    IProjectApplicationRepository,
    IProjectRepository,
)
from app.domain.review.enums import ReviewStatus


class SubmitRatingUseCase(UseCase[SubmitRatingCommand, SubmitRatingResult]):
    def __init__(
        self,
        authorization_service: IAuthorizationService,
        project_repo: IProjectRepository,
        application_repo: IProjectApplicationRepository,
        customer_review_repo: ICustomerReviewRepository,
        rating_repo: IRatingRepository,
        id_generator: IIdGenerator,
        clock: IClock,
        uow: IUnitOfWork,
    ) -> None:
        self._authorization_service = authorization_service
        self._project_repo = project_repo
        self._application_repo = application_repo
        self._customer_review_repo = customer_review_repo
        self._rating_repo = rating_repo
        self._id_generator = id_generator
        self._clock = clock
        self._uow = uow

    async def execute(self, request: SubmitRatingCommand) -> SubmitRatingResult:
        project = await self._project_repo.get_by_id(request.project_id)
        await authorize_owned_action(
            self._authorization_service,
            request.actor_id,
            project.customer_user_id,
            PERMISSION_FEEDBACK_MANAGE_OWN,
            PERMISSION_FEEDBACK_MANAGE_ANY,
        )
        if project.status != ProjectStatus.COMPLETED:
            raise ProjectNotCompletedError(
                f"Project {project.id} is '{project.status.value}'; it can only be rated after completion."
            )
        if await self._rating_repo.find_by_project(project.id) is not None:
            raise RatingAlreadyExistsError(f"Project {project.id} has already been rated.")
        if project.selected_application_id is None:
            raise ValidationError(f"Project {project.id} has no selected freelancer to rate.")
        application = await self._application_repo.get_by_id(project.selected_application_id)
        reviews = await self._customer_review_repo.list_by_project(project.id)
        approved_reviews = [r for r in reviews if r.decision == ReviewStatus.APPROVED]
        if not approved_reviews:
            latest = reviews[0] if reviews else None
            if latest is None:
                raise ValidationError(
                    f"Project {project.id} has no customer review yet; submit a review before rating."
                )
            raise CustomerReviewNotApprovedError(
                f"Project {project.id} cannot be rated until its customer review is "
                f"approved (current decision: '{latest.decision.value}')."
            )
        customer_review = approved_reviews[0]
        now = await self._clock.now()
        rating = Rating(
            id=await self._id_generator.new_id(),
            customer_review_id=customer_review.id,
            project_id=project.id,
            customer_user_id=request.actor_id,
            freelancer_profile_id=application.freelancer_profile_id,
            score=request.score,
            comment=request.comment,
            is_public=request.is_public,
            created_at=now,
        )
        async with self._uow:
            await self._rating_repo.add(rating)
            await self._uow.commit()
        return SubmitRatingResult(
            rating_id=rating.id,
            project_id=project.id,
            score=rating.score,
        )
