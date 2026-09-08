"""Health-endpoint tests (Phase B, no dataset required)."""

from __future__ import annotations

from fastapi.testclient import TestClient

from apps.api import __version__
from apps.api.main import create_app
from apps.api.settings import Settings, get_settings


def _client(environment: str) -> TestClient:
    app = create_app()
    settings = Settings(environment=environment)
    app.dependency_overrides[get_settings] = lambda: settings
    return TestClient(app)


def test_health_ok() -> None:
    client = _client("test")
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["service"] == "autoinspect-api"
    assert body["environment"] == "test"
    assert body["version"] == __version__


def test_health_reports_env_environment() -> None:
    client = _client("production")
    body = client.get("/health").json()
    assert body["environment"] == "production"


def test_cors_allows_only_configured_origins() -> None:
    app = create_app(Settings(environment="test", cors_origins=["http://localhost:3000"]))
    client = TestClient(app)

    preflight = client.options(
        "/health",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert preflight.status_code in (200, 400)
    assert preflight.headers.get("access-control-allow-origin") == "http://localhost:3000"

    disallowed = client.options(
        "/health",
        headers={
            "Origin": "https://evil.example",
            "Access-Control-Request-Method": "GET",
        },
    )
    allow = disallowed.headers.get("access-control-allow-origin")
    assert allow is None or allow == "http://localhost:3000"
