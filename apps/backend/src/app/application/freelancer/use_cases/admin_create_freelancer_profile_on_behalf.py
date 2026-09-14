from app.application.freelancer.dto import (
    CreateFreelancerProfileOnBehalfCommand,
    CreateFreelancerProfileResult,
)
from app.application.freelancer.permissions import PERMISSION_FREELANCER_CREATE_ON_BEHALF
from app.application.freelancer.use_cases.create_freelancer_profile import (
    _create_freelancer_profile,
)
from app.application.shared.authorization import IAuthorizationService
from app.application.shared.ports import IClock, IIdGenerator, IUnitOfWork
from app.application.shared.use_case import UseCase
from app.domain.freelancer.repositories import IFreelancerProfileRepository
from app.domain.iam.repositories import IUserRepository


class AdminCreateFreelancerProfileOnBehalfUseCase(
    UseCase[CreateFreelancerProfileOnBehalfCommand, CreateFreelancerProfileResult]
):
    def __init__(
        self,
        authorization_service: IAuthorizationService,
        user_repo: IUserRepository,
        profile_repo: IFreelancerProfileRepository,
        id_generator: IIdGenerator,
        clock: IClock,
        uow: IUnitOfWork,
    ) -> None:
        self._authorization_service = authorization_service
        self._user_repo = user_repo
        self._profile_repo = profile_repo
        self._id_generator = id_generator
        self._clock = clock
        self._uow = uow

    async def execute(self, request: CreateFreelancerProfileOnBehalfCommand) -> CreateFreelancerProfileResult:
        await self._authorization_service.require_permission(request.actor_id, PERMISSION_FREELANCER_CREATE_ON_BEHALF)
        await self._user_repo.get_by_id(request.target_user_id)
        request.validate()
        return await _create_freelancer_profile(
            user_id=request.target_user_id,
            created_by_user_id=request.actor_id,
            display_name=request.display_name,
            headline=request.headline,
            bio=request.bio,
            country_code=request.country_code,
            city=request.city,
            timezone=request.timezone,
            profile_repo=self._profile_repo,
            id_generator=self._id_generator,
            clock=self._clock,
            uow=self._uow,
        )
