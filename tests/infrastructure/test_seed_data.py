from app.infrastructure.seed.seed_data import ROLE_PERMISSIONS


def test_freelancer_role_can_read_its_own_profile_resources() -> None:
    assert "freelancer.read_own" in ROLE_PERMISSIONS["freelancer"]
    assert "freelancer.read_any" not in ROLE_PERMISSIONS["freelancer"]
