"""CORS preflight tests.

Per PRESENTATION.md §9 the app registers FastAPI's ``CORSMiddleware`` with
origins read from ``Settings``. ``create_app()`` defaults to the local dev
origin ``http://localhost:3000`` when no origins are injected.
"""

from fastapi.testclient import TestClient


def test_cors_preflight_register(client: TestClient) -> None:
    resp = client.options(
        "/api/v1/auth/register",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "POST",
        },
    )
    assert resp.status_code == 200
    assert resp.headers["access-control-allow-origin"] == "http://localhost:3000"
    assert resp.headers["access-control-allow-credentials"] == "true"


def test_cors_disallows_unlisted_origin(client: TestClient) -> None:
    resp = client.options(
        "/api/v1/auth/register",
        headers={
            "Origin": "https://evil.example.com",
            "Access-Control-Request-Method": "POST",
        },
    )
    assert "access-control-allow-origin" not in resp.headers