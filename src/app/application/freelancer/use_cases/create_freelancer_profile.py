from app.application.freelancer.dto import (
    CreateFreelancerProfileCommand,
    CreateFreelancerProfileResult,
)
from app.application.freelancer.permissions import PERMISSION_FREELANCER_CREATE_OWN
from app.application.shared.authorization import IAuthorizationService
from app.application.shared.ports import IClock, IIdGenerator, IUnitOfWork
from app.application.shared.use_case import UseCase
from app.domain.freelancer.entities import FreelancerProfile
from app.domain.freelancer.enums import FreelancerApprovalStatus
from app.domain.freelancer.exceptions import (
    DuplicateFreelancerProfileError,
    FreelancerProfileNotFoundError,
)
from app.domain.freelancer.repositories import IFreelancerProfileRepository


async def _create_freelancer_profile(
    *,
    user_id: str,
    created_by_user_id: str,
    display_name: str,
    headline: str | None,
    bio: str | None,
    country_code: str | None,
    city: str | None,
    timezone: str | None,
    profile_repo: IFreelancerProfileRepository,
    id_generator: IIdGenerator,
    clock: IClock,
    uow: IUnitOfWork,
) -> CreateFreelancerProfileResult:
    try:
        await profile_repo.get_by_user_id(user_id)
    except FreelancerProfileNotFoundError:
        pass
    else:
        raise DuplicateFreelancerProfileError(f"A freelancer profile already exists for user {user_id}.")
    now = await clock.now()
    profile = FreelancerProfile(
        id=await id_generator.new_id(),
        user_id=user_id,
        current_level_id=None,
        approval_status=FreelancerApprovalStatus.PENDING,
        approved_by_user_id=None,
        approved_at=None,
        approval_note=None,
        display_name=display_name,
        headline=headline,
        bio=bio,
        country_code=country_code,
        city=city,
        timezone=timezone,
        hourly_rate_min=None,
        hourly_rate_max=None,
        is_available=True,
        deleted_at=None,
        created_by_user_id=created_by_user_id,
        created_at=now,
    )
    async with uow:
        await profile_repo.add(profile)
        await uow.commit()
    return CreateFreelancerProfileResult(profile_id=profile.id)


class CreateFreelancerProfileUseCase(UseCase[CreateFreelancerProfileCommand, CreateFreelancerProfileResult]):
    def __init__(
        self,
        authorization_service: IAuthorizationService,
        profile_repo: IFreelancerProfileRepository,
        id_generator: IIdGenerator,
        clock: IClock,
        uow: IUnitOfWork,
    ) -> None:
        self._authorization_service = authorization_service
        self._profile_repo = profile_repo
        self._id_generator = id_generator
        self._clock = clock
        self._uow = uow

    async def execute(self, request: CreateFreelancerProfileCommand) -> CreateFreelancerProfileResult:
        await self._authorization_service.require_permission(request.user_id, PERMISSION_FREELANCER_CREATE_OWN)
        request.validate()
        return await _create_freelancer_profile(
            user_id=request.user_id,
            created_by_user_id=request.user_id,
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
