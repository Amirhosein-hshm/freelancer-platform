"""``GET /api/v1/auth/me`` shape + roles/permissions exclusivity tests.

Per API_DESIGN.md §6: only ``/auth/me`` may return ``roles``/``permissions`` in
its ``data``; no other endpoint includes them.
"""

from datetime import UTC, datetime

from fastapi.testclient import TestClient

from app.domain.iam.entities import User
from app.domain.iam.enums import UserStatus
from app.domain.iam.value_objects import Email, PasswordHash
from app.presentation.core import providers
from tests.fakes.fake_user_repository import FakeUserRepository
from tests.presentation.conftest import auth_header

NOW = datetime(2026, 8, 2, tzinfo=UTC)


def _seed_user(user_repo: FakeUserRepository) -> None:
    user = User(
        id="user-1",
        created_at=NOW,
        email=Email("me@example.com"),
        phone=None,
        password_hash=PasswordHash("fake-hash:secret"),
        first_name="Jane",
        last_name="Doe",
        status=UserStatus.ACTIVE,
    )
    user_repo._store[user.id] = user
    user_repo._by_email[user.email.value] = user


def test_get_me_returns_roles_and_permissions(client: TestClient, overrides) -> None:
    _seed_user(overrides[providers.get_user_repository])
    authz = overrides[providers.get_authorization_service]
    authz.grant("user-1", "project.create_own")
    authz.grant("user-1", "project.apply")
    authz.assign_role("user-1", "customer")

    headers = auth_header(None, "user-1", ["customer"])
    resp = client.get("/api/v1/auth/me", headers=headers)

    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert body["meta"] is None
    data = body["data"]
    assert data["user_id"] == "user-1"
    assert data["email"] == "me@example.com"
    assert data["roles"] == ["customer"]
    assert set(data["permissions"]) == {"project.create_own", "project.apply"}


def test_only_auth_me_endpoint_exposes_roles_and_permissions(
    client: TestClient, overrides
) -> None:
    _seed_user(overrides[providers.get_user_repository])
    authz = overrides[providers.get_authorization_service]
    authz.grant("user-1", "project.create_own")
    authz.assign_role("user-1", "customer")

    headers = auth_header(None, "user-1", ["customer"])
    me_resp = client.get("/api/v1/auth/me", headers=headers)
    assert "roles" in me_resp.json()["data"]
    assert "permissions" in me_resp.json()["data"]

    login_resp = client.post(
        "/api/v1/auth/login", json={"email": "me@example.com", "password": "secret"}
    )
    assert login_resp.status_code == 200
    assert "roles" not in login_resp.json()["data"]
    assert "permissions" not in login_resp.json()["data"]


def test_get_me_requires_authentication(client: TestClient) -> None:
    resp = client.get("/api/v1/auth/me")
    assert resp.status_code == 401