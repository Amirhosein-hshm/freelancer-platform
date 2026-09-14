from app.infrastructure.seed.seed_data import ROLE_PERMISSIONS


def test_freelancer_role_can_read_its_own_profile_resources() -> None:
    assert "freelancer.read_own" in ROLE_PERMISSIONS["freelancer"]
    assert "freelancer.read_any" not in ROLE_PERMISSIONS["freelancer"]


def test_freelancer_role_can_read_public_projects() -> None:
    assert "project.read_public" in ROLE_PERMISSIONS["freelancer"]


def test_supervisor_role_can_read_and_close_own_tickets_only() -> None:
    assert "ticket.read_own" in ROLE_PERMISSIONS["supervisor"]
    assert "ticket.close_own" in ROLE_PERMISSIONS["supervisor"]
    assert "ticket.read_any" not in ROLE_PERMISSIONS["supervisor"]
    assert "ticket.close_any" not in ROLE_PERMISSIONS["supervisor"]
