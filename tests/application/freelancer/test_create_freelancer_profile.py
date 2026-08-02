import pytest

from app.application.freelancer.dto import CreateFreelancerProfileCommand
from app.application.freelancer.use_cases.create_freelancer_profile import (
    CreateFreelancerProfileUseCase,
)
from app.application.shared.exceptions import ValidationError
from app.domain.freelancer.enums import FreelancerApprovalStatus
from app.domain.freelancer.exceptions import DuplicateFreelancerProfileError


def build_use_case(profile_repo, id_generator, clock, uow) -> CreateFreelancerProfileUseCase:
    return CreateFreelancerProfileUseCase(
        profile_repo=profile_repo, id_generator=id_generator, clock=clock, uow=uow
    )


class TestCreateFreelancerProfileUseCase:
    def test_create_profile_succeeds(self, profile_repo, id_generator, clock, uow):
        use_case = build_use_case(profile_repo, id_generator, clock, uow)

        result = use_case.execute(
            CreateFreelancerProfileCommand(user_id="user-1", display_name="Jane Dev", city="Tehran")
        )

        profile = profile_repo.get_by_user_id("user-1")
        assert result.profile_id == profile.id
        assert profile.approval_status == FreelancerApprovalStatus.PENDING
        assert profile.display_name == "Jane Dev"
        assert profile.city == "Tehran"
        assert profile.is_available is True
        assert uow.committed is True

    def test_duplicate_profile_raises(
        self, profile_repo, id_generator, clock, uow, make_profile
    ):
        make_profile(user_id="user-1")
        use_case = build_use_case(profile_repo, id_generator, clock, uow)

        with pytest.raises(DuplicateFreelancerProfileError):
            use_case.execute(
                CreateFreelancerProfileCommand(user_id="user-1", display_name="Jane Dev")
            )

    def test_missing_display_name_raises_validation(
        self, profile_repo, id_generator, clock, uow
    ):
        use_case = build_use_case(profile_repo, id_generator, clock, uow)

        with pytest.raises(ValidationError):
            use_case.execute(CreateFreelancerProfileCommand(user_id="user-1", display_name="  "))
