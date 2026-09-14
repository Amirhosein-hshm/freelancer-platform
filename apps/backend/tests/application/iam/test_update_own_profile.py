import pytest

from app.application.iam.dto import UpdateOwnProfileCommand
from app.application.iam.use_cases.update_own_profile import UpdateOwnProfileUseCase
from app.domain.iam.value_objects import Email
from app.application.shared.exceptions import ValidationError


@pytest.mark.asyncio
async def test_user_can_update_own_profile(user_repo, make_user, uow):
    user = await make_user(email="original@example.com")
    result = await UpdateOwnProfileUseCase(user_repo, uow).execute(
        UpdateOwnProfileCommand(actor_id=user.id, first_name="Updated", phone="+15551234567")
    )

    assert result.first_name == "Updated"
    assert result.last_name == "Doe"
    assert result.phone == "+15551234567"
    saved = await user_repo.get_by_id(user.id)
    assert saved.email == Email("original@example.com")


@pytest.mark.asyncio
async def test_empty_profile_name_is_rejected(user_repo, make_user, uow):
    user = await make_user()
    with pytest.raises(ValidationError):
        await UpdateOwnProfileUseCase(user_repo, uow).execute(
            UpdateOwnProfileCommand(actor_id=user.id, first_name=" ")
        )
