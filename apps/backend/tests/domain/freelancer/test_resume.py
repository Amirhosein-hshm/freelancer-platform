from datetime import UTC, datetime

from app.domain.freelancer.entities import Resume

NOW = datetime(2026, 8, 2, tzinfo=UTC)


def make_resume(**overrides: object) -> Resume:
    fields: dict[str, object] = {
        "id": "resume-1",
        "freelancer_profile_id": "profile-1",
        "file_asset_id": "asset-1",
        "version_no": 1,
        "summary": None,
        "is_current": True,
        "created_at": NOW,
    }
    fields.update(overrides)
    return Resume(**fields)  # type: ignore[arg-type]


class TestResume:
    def test_mark_as_current(self):
        resume = make_resume(is_current=False)
        resume.mark_as_current()
        assert resume.is_current is True

    def test_identity_is_id(self):
        resume = make_resume(id="r-1")
        assert hash(resume) == hash("r-1")
        assert resume == make_resume(id="r-1")
