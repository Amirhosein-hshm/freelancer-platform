import pytest

from app.application.freelancer.dto import UploadResumeCommand
from app.application.freelancer.use_cases.upload_resume import UploadResumeUseCase
from app.application.shared.exceptions import ValidationError
from app.domain.freelancer.exceptions import FreelancerProfileNotFoundError


def build_use_case(profile_repo, resume_repo, file_storage, id_generator, clock, uow):
    return UploadResumeUseCase(
        profile_repo=profile_repo,
        resume_repo=resume_repo,
        file_storage=file_storage,
        id_generator=id_generator,
        clock=clock,
        uow=uow,
    )


class TestUploadResumeUseCase:
    async def test_first_upload_creates_version_one(
        self, profile_repo, resume_repo, file_storage, id_generator, clock, uow, make_profile, make_asset
    ):
        await make_profile(user_id="user-1")
        make_asset("asset-1")
        use_case = build_use_case(profile_repo, resume_repo, file_storage, id_generator, clock, uow)

        result = await use_case.execute(UploadResumeCommand(user_id="user-1", file_asset_id="asset-1", summary="v1"))

        assert result.version_no == 1
        current = await resume_repo.get_current("profile-1")
        assert current is not None
        assert current.file_asset_id == "asset-1"
        assert current.summary == "v1"
        assert uow.committed is True

    async def test_second_upload_increments_version_and_demotes_previous(
        self,
        profile_repo,
        resume_repo,
        file_storage,
        id_generator,
        clock,
        uow,
        make_profile,
        make_asset,
    ):
        await make_profile(user_id="user-1")
        make_asset("asset-1")
        make_asset("asset-2")
        use_case = build_use_case(profile_repo, resume_repo, file_storage, id_generator, clock, uow)

        first = await use_case.execute(UploadResumeCommand(user_id="user-1", file_asset_id="asset-1"))
        second = await use_case.execute(UploadResumeCommand(user_id="user-1", file_asset_id="asset-2", summary="v2"))

        assert first.version_no == 1
        assert second.version_no == 2
        assert (await resume_repo.get_current("profile-1")).file_asset_id == "asset-2"
        assert len(await resume_repo.list_by_profile("profile-1")) == 2
        assert [r.version_no for r in await resume_repo.list_by_profile("profile-1")] == [1, 2]

    async def test_missing_file_asset_raises_validation(
        self, profile_repo, resume_repo, file_storage, id_generator, clock, uow, make_profile
    ):
        await make_profile(user_id="user-1")
        use_case = build_use_case(profile_repo, resume_repo, file_storage, id_generator, clock, uow)

        with pytest.raises(ValidationError):
            await use_case.execute(UploadResumeCommand(user_id="user-1", file_asset_id="ghost"))

    async def test_unknown_profile_raises(
        self, profile_repo, resume_repo, file_storage, id_generator, clock, uow, make_asset
    ):
        make_asset("asset-1")
        use_case = build_use_case(profile_repo, resume_repo, file_storage, id_generator, clock, uow)

        with pytest.raises(FreelancerProfileNotFoundError):
            await use_case.execute(UploadResumeCommand(user_id="ghost", file_asset_id="asset-1"))
