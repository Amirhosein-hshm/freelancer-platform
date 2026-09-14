import pytest

from app.application.freelancer.dto import CreateFreelancerProfileCommand
from app.application.freelancer.use_cases.create_freelancer_profile import (
    CreateFreelancerProfileUseCase,
)
from app.application.shared.exceptions import PermissionDeniedError, ValidationError
from app.domain.freelancer.enums import FreelancerApprovalStatus
from app.domain.freelancer.exceptions import DuplicateFreelancerProfileError


def build_use_case(authorization_service, profile_repo, id_generator, clock, uow) -> CreateFreelancerProfileUseCase:
    return CreateFreelancerProfileUseCase(
        authorization_service=authorization_service,
        profile_repo=profile_repo,
        id_generator=id_generator,
        clock=clock,
        uow=uow,
    )


class TestCreateFreelancerProfileUseCase:
    async def test_create_profile_succeeds(self, authorization_service, profile_repo, id_generator, clock, uow):
        authorization_service.grant("user-1", "freelancer.create_own")
        use_case = build_use_case(authorization_service, profile_repo, id_generator, clock, uow)

        result = await use_case.execute(
            CreateFreelancerProfileCommand(user_id="user-1", display_name="Jane Dev", city="Tehran")
        )

        profile = await profile_repo.get_by_user_id("user-1")
        assert result.profile_id == profile.id
        assert profile.approval_status == FreelancerApprovalStatus.PENDING
        assert profile.display_name == "Jane Dev"
        assert profile.city == "Tehran"
        assert profile.is_available is True
        assert profile.created_by_user_id == "user-1"
        assert uow.committed is True

    async def test_without_permission_raises(self, authorization_service, profile_repo, id_generator, clock, uow):
        use_case = build_use_case(authorization_service, profile_repo, id_generator, clock, uow)

        with pytest.raises(PermissionDeniedError):
            await use_case.execute(CreateFreelancerProfileCommand(user_id="user-1", display_name="Jane Dev"))

    async def test_duplicate_profile_raises(
        self, authorization_service, profile_repo, id_generator, clock, uow, make_profile
    ):
        authorization_service.grant("user-1", "freelancer.create_own")
        await make_profile(user_id="user-1")
        use_case = build_use_case(authorization_service, profile_repo, id_generator, clock, uow)

        with pytest.raises(DuplicateFreelancerProfileError):
            await use_case.execute(CreateFreelancerProfileCommand(user_id="user-1", display_name="Jane Dev"))

    async def test_missing_display_name_raises_validation(
        self, authorization_service, profile_repo, id_generator, clock, uow
    ):
        authorization_service.grant("user-1", "freelancer.create_own")
        use_case = build_use_case(authorization_service, profile_repo, id_generator, clock, uow)

        with pytest.raises(ValidationError):
            await use_case.execute(CreateFreelancerProfileCommand(user_id="user-1", display_name="  "))
