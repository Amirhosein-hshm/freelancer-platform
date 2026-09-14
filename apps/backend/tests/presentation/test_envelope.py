"""Envelope shape tests: one success and one error per HTTP status code.

Per TESTING.md §9 and API_DESIGN.md §2-§4, every endpoint must return a fixed
``SuccessEnvelope``/``ErrorEnvelope`` shape and the exception handler must map
exceptions to the documented HTTP status codes (404/409/422/403/400).
"""

from fastapi.testclient import TestClient

from app.domain.iam.entities import Role, User
from app.domain.iam.enums import UserStatus
from app.domain.iam.value_objects import Email, PasswordHash
from app.presentation.core import providers
from tests.fakes.fake_user_repository import FakeUserRepository
from tests.presentation.conftest import NOW, auth_header


def _seed_user(user_repo: FakeUserRepository, email: str = "user@example.com") -> None:
    user = User(
        id="user-1",
        created_at=NOW,
        email=Email(email),
        phone=None,
        password_hash=PasswordHash("fake-hash:secret"),
        first_name="Jane",
        last_name="Doe",
        status=UserStatus.ACTIVE,
    )
    # store into FakeUserRepository synchronously
    user_repo._store[user.id] = user
    user_repo._by_email[user.email.value] = user


def test_login_success_envelope(client: TestClient, overrides):
    _seed_user(overrides[providers.get_user_repository])
    resp = client.post("/api/v1/auth/login", json={"email": "user@example.com", "password": "secret"})
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert isinstance(body["message"], str) and body["message"]
    assert isinstance(body["data"], dict)
    assert body["meta"] is None
    assert "access_token" in body["data"]
    assert "refresh_token" in body["data"]


def test_404_entity_not_found(client: TestClient) -> None:
    headers = auth_header(None, "user-1", ["customer"])
    resp = client.get("/api/v1/projects/does-not-exist", headers=headers)
    assert resp.status_code == 404
    body = resp.json()
    assert body["success"] is False
    assert body["error"]["code"] == "PROJECT_NOT_FOUND"
    assert isinstance(body["error"]["message"], str)


def test_409_duplicate_email(client: TestClient, overrides) -> None:
    role_repo = overrides[providers.get_role_repository]
    _seed_role(role_repo)
    user = User(
        id="user-1",
        created_at=NOW,
        email=Email("dupe@example.com"),
        phone=None,
        password_hash=PasswordHash("fake-hash:secret"),
        first_name="Jane",
        last_name="Doe",
        status=UserStatus.PENDING,
    )
    user_repo: FakeUserRepository = overrides[providers.get_user_repository]
    user_repo._store[user.id] = user
    user_repo._by_email[user.email.value] = user
    payload = {
        "email": "dupe@example.com",
        "password": "password1",
        "first_name": "Jane",
        "last_name": "Doe",
        "role": "customer",
    }
    resp = client.post("/api/v1/auth/register", json=payload)
    assert resp.status_code == 409
    body = resp.json()
    assert body["success"] is False
    assert body["error"]["code"] == "DUPLICATE_EMAIL"


def test_422_business_rule(client: TestClient, overrides) -> None:
    _seed_user(overrides[providers.get_user_repository])
    resp = client.post("/api/v1/auth/login", json={"email": "user@example.com", "password": "wrong"})
    assert resp.status_code == 422
    body = resp.json()
    assert body["success"] is False
    assert body["error"]["code"] == "INVALID_CREDENTIALS"


def test_403_permission_denied(client: TestClient) -> None:
    headers = auth_header(None, "user-1", ["customer"])
    resp = client.get("/api/v1/reporting/dashboard", headers=headers)
    assert resp.status_code == 403
    body = resp.json()
    assert body["success"] is False
    assert body["error"]["code"] == "PERMISSION_DENIED"


def test_400_validation_error(client: TestClient) -> None:
    resp = client.post("/api/v1/auth/login", json={"email": "", "password": ""})
    assert resp.status_code == 400
    body = resp.json()
    assert body["success"] is False
    assert body["error"]["code"] == "VALIDATION"


def _seed_role(role_repo) -> None:
    role_repo._store["role-customer"] = Role(
        id="role-customer",
        role_key="customer",
        name="Customer",
        created_at=NOW,
    )
    role_repo._by_key["customer"] = role_repo._store["role-customer"]
