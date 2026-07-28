from __future__ import annotations

from fastapi.testclient import TestClient

from backend.app import create_app
from backend.config import Settings


class FakeArchitecture:
    def generate(self, prompt: str) -> dict[str, object]:
        return {
            "requirements": {"functional": [prompt]},
            "design": {"system_name": "Test", "tech_stack": []},
            "mermaid": "flowchart LR\nA[Client] --> B[API]",
            "critique_iterations": 2,
        }


class FakePricing:
    def estimate(self, design: dict[str, object]) -> tuple[float, list[str]]:
        return 12.5, ["Test: $12.50/mo"]


def settings(**overrides: object) -> Settings:
    values: dict[str, object] = {
        "openrouter_api_key": "test-key",
        "infracost_api_key": None,
        "cors_origins": ["http://localhost:8501"],
        "max_prompt_chars": 100,
        "rate_limit_per_minute": 0,
    }
    values.update(overrides)
    return Settings(**values)


def test_health_and_readiness_endpoints() -> None:
    client = TestClient(create_app(settings(), FakeArchitecture(), FakePricing()))
    assert client.get("/health").json() == {"status": "ok"}
    assert client.get("/ready").status_code == 200


def test_missing_required_key_fails_readiness_and_chat() -> None:
    client = TestClient(
        create_app(settings(openrouter_api_key=None), FakeArchitecture(), FakePricing())
    )
    assert client.get("/ready").status_code == 503
    response = client.post("/chat", json={"user_input": "Build chat"})
    assert response.status_code == 503
    assert response.json()["error"]["code"] == "service_not_ready"


def test_chat_contract_and_request_id() -> None:
    client = TestClient(create_app(settings(), FakeArchitecture(), FakePricing()))
    response = client.post("/chat", json={"user_input": "Build chat"})
    body = response.json()
    assert response.status_code == 200
    assert response.headers["x-request-id"] == body["request_id"]
    assert body["thread_id"]
    assert body["critique_iterations"] == 2
    assert body["estimated_monthly_cost_usd"] == 12.5


def test_prompt_size_is_bounded() -> None:
    client = TestClient(create_app(settings(max_prompt_chars=5), FakeArchitecture(), FakePricing()))
    response = client.post("/chat", json={"user_input": "123456"})
    assert response.status_code == 413
    assert response.json()["error"]["code"] == "prompt_too_large"


def test_cors_is_restricted() -> None:
    client = TestClient(create_app(settings(), FakeArchitecture(), FakePricing()))
    allowed = client.options(
        "/chat",
        headers={"Origin": "http://localhost:8501", "Access-Control-Request-Method": "POST"},
    )
    denied = client.options(
        "/chat", headers={"Origin": "https://evil.example", "Access-Control-Request-Method": "POST"}
    )
    assert allowed.headers.get("access-control-allow-origin") == "http://localhost:8501"
    assert denied.headers.get("access-control-allow-origin") is None
