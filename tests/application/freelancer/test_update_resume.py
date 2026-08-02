import pytest

from app.application.freelancer.dto import UpdateResumeCommand
from app.application.freelancer.use_cases.update_resume import UpdateResumeUseCase
from app.domain.freelancer.entities import Resume
from app.domain.freelancer.exceptions import ResumeNotFoundError
from tests.application.freelancer.conftest import NOW


def build_use_case(profile_repo, resume_repo) -> UpdateResumeUseCase:
    return UpdateResumeUseCase(profile_repo=profile_repo, resume_repo=resume_repo)


def seed_resume(resume_repo, profile_id: str = "profile-1") -> Resume:
    resume = Resume(
        id="resume-1",
        freelancer_profile_id=profile_id,
        file_asset_id="asset-1",
        version_no=1,
        summary="old summary",
        is_current=True,
        created_at=NOW,
    )
    resume_repo.add(resume)
    return resume


class TestUpdateResumeUseCase:
    def test_update_summary(self, profile_repo, resume_repo, make_profile):
        make_profile(user_id="user-1")
        seed_resume(resume_repo)
        use_case = build_use_case(profile_repo, resume_repo)

        result = use_case.execute(UpdateResumeCommand(user_id="user-1", summary="new summary"))

        assert result.resume_id == "resume-1"
        assert result.summary == "new summary"
        assert resume_repo.get_current("profile-1").summary == "new summary"

    def test_clear_summary(self, profile_repo, resume_repo, make_profile):
        make_profile(user_id="user-1")
        seed_resume(resume_repo)
        use_case = build_use_case(profile_repo, resume_repo)

        result = use_case.execute(UpdateResumeCommand(user_id="user-1", summary=None))

        assert result.summary is None

    def test_no_current_resume_raises(self, profile_repo, resume_repo, make_profile):
        make_profile(user_id="user-1")
        use_case = build_use_case(profile_repo, resume_repo)

        with pytest.raises(ResumeNotFoundError):
            use_case.execute(UpdateResumeCommand(user_id="user-1", summary="x"))
