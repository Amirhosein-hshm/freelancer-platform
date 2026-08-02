from app.application.freelancer.dto import (
    CreateFreelancerProfileCommand,
    CreateFreelancerProfileResult,
)
from app.application.shared.ports import IClock, IIdGenerator, IUnitOfWork
from app.application.shared.use_case import UseCase
from app.domain.freelancer.entities import FreelancerProfile
from app.domain.freelancer.enums import FreelancerApprovalStatus
from app.domain.freelancer.exceptions import (
    DuplicateFreelancerProfileError,
    FreelancerProfileNotFoundError,
)
from app.domain.freelancer.repositories import IFreelancerProfileRepository


class CreateFreelancerProfileUseCase(
    UseCase[CreateFreelancerProfileCommand, CreateFreelancerProfileResult]
):
    def __init__(
        self,
        profile_repo: IFreelancerProfileRepository,
        id_generator: IIdGenerator,
        clock: IClock,
        uow: IUnitOfWork,
    ) -> None:
        self._profile_repo = profile_repo
        self._id_generator = id_generator
        self._clock = clock
        self._uow = uow

    def execute(self, request: CreateFreelancerProfileCommand) -> CreateFreelancerProfileResult:
        request.validate()
        try:
            self._profile_repo.get_by_user_id(request.user_id)
        except FreelancerProfileNotFoundError:
            pass
        else:
            raise DuplicateFreelancerProfileError(
                f"A freelancer profile already exists for user {request.user_id}."
            )
        now = self._clock.now()
        profile = FreelancerProfile(
            id=self._id_generator.new_id(),
            user_id=request.user_id,
            current_level_id=None,
            approval_status=FreelancerApprovalStatus.PENDING,
            approved_by_user_id=None,
            approved_at=None,
            approval_note=None,
            display_name=request.display_name,
            headline=request.headline,
            bio=request.bio,
            country_code=request.country_code,
            city=request.city,
            timezone=request.timezone,
            hourly_rate_min=None,
            hourly_rate_max=None,
            is_available=True,
            deleted_at=None,
            created_at=now,
        )
        with self._uow:
            self._profile_repo.add(profile)
            self._uow.commit()
        return CreateFreelancerProfileResult(profile_id=profile.id)
