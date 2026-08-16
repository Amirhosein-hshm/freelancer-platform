from datetime import UTC, datetime

import pytest

from app.application.freelancer.dto import CreateFreelancerProfileOnBehalfCommand
from app.application.freelancer.use_cases.admin_create_freelancer_profile_on_behalf import (
    AdminCreateFreelancerProfileOnBehalfUseCase,
)
from app.application.shared.exceptions import PermissionDeniedError, ValidationError
from app.domain.freelancer.enums import FreelancerApprovalStatus
from app.domain.freelancer.exceptions import DuplicateFreelancerProfileError
from app.domain.iam.entities import User
from app.domain.iam.enums import UserStatus
from app.domain.iam.exceptions import UserNotFoundError
from app.domain.iam.value_objects import Email, PasswordHash
from tests.fakes.fake_user_repository import FakeUserRepository

NOW = datetime(2026, 8, 2, tzinfo=UTC)


@pytest.fixture
def user_repo() -> FakeUserRepository:
    return FakeUserRepository()


def build_use_case(authorization_service, user_repo, profile_repo, id_generator, clock, uow):
    return AdminCreateFreelancerProfileOnBehalfUseCase(
        authorization_service=authorization_service,
        user_repo=user_repo,
        profile_repo=profile_repo,
        id_generator=id_generator,
        clock=clock,
        uow=uow,
    )


async def seed_user(user_repo, user_id: str = "freelancer-1") -> None:
    await user_repo.add(
        User(
            id=user_id,
            email=Email("user@example.com"),
            phone=None,
            password_hash=PasswordHash("hashed"),
            first_name="Jane",
            last_name="Dev",
            status=UserStatus.ACTIVE,
            created_at=NOW,
        )
    )


class TestAdminCreateFreelancerProfileOnBehalfUseCase:
    async def test_admin_creates_profile_for_target_user(
        self, authorization_service, user_repo, profile_repo, id_generator, clock, uow
    ):
        authorization_service.grant("admin-1", "freelancer.create_on_behalf")
        await seed_user(user_repo)
        use_case = build_use_case(authorization_service, user_repo, profile_repo, id_generator, clock, uow)

        result = await use_case.execute(
            CreateFreelancerProfileOnBehalfCommand(
                actor_id="admin-1",
                target_user_id="freelancer-1",
                display_name="Jane Dev",
            )
        )

        profile = await profile_repo.get_by_id(result.profile_id)
        assert profile.user_id == "freelancer-1"
        assert profile.created_by_user_id == "admin-1"
        assert profile.approval_status == FreelancerApprovalStatus.PENDING
        assert uow.committed is True

    async def test_without_permission_raises(
        self, authorization_service, user_repo, profile_repo, id_generator, clock, uow
    ):
        use_case = build_use_case(authorization_service, user_repo, profile_repo, id_generator, clock, uow)

        with pytest.raises(PermissionDeniedError):
            await use_case.execute(
                CreateFreelancerProfileOnBehalfCommand(
                    actor_id="freelancer-1",
                    target_user_id="freelancer-2",
                    display_name="Jane Dev",
                )
            )

    async def test_nonexistent_target_user_raises(
        self, authorization_service, user_repo, profile_repo, id_generator, clock, uow
    ):
        authorization_service.grant("admin-1", "freelancer.create_on_behalf")
        use_case = build_use_case(authorization_service, user_repo, profile_repo, id_generator, clock, uow)

        with pytest.raises(UserNotFoundError):
            await use_case.execute(
                CreateFreelancerProfileOnBehalfCommand(
                    actor_id="admin-1",
                    target_user_id="missing-user",
                    display_name="Jane Dev",
                )
            )

    async def test_duplicate_target_profile_raises(
        self, authorization_service, user_repo, profile_repo, id_generator, clock, uow, make_profile
    ):
        authorization_service.grant("admin-1", "freelancer.create_on_behalf")
        await seed_user(user_repo)
        await make_profile(profile_id="profile-1", user_id="freelancer-1")
        use_case = build_use_case(authorization_service, user_repo, profile_repo, id_generator, clock, uow)

        with pytest.raises(DuplicateFreelancerProfileError):
            await use_case.execute(
                CreateFreelancerProfileOnBehalfCommand(
                    actor_id="admin-1",
                    target_user_id="freelancer-1",
                    display_name="Jane Dev",
                )
            )

    async def test_missing_display_name_raises_validation(
        self, authorization_service, user_repo, profile_repo, id_generator, clock, uow
    ):
        authorization_service.grant("admin-1", "freelancer.create_on_behalf")
        await seed_user(user_repo)
        use_case = build_use_case(authorization_service, user_repo, profile_repo, id_generator, clock, uow)

        with pytest.raises(ValidationError):
            await use_case.execute(
                CreateFreelancerProfileOnBehalfCommand(
                    actor_id="admin-1",
                    target_user_id="freelancer-1",
                    display_name="  ",
                )
            )
