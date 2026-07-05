from fastapi.testclient import TestClient

from app.main import app


def test_health() -> None:
    response = TestClient(app).get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_research_requires_api_key(monkeypatch) -> None:
    from types import SimpleNamespace

    monkeypatch.setattr("app.main.get_settings", lambda: SimpleNamespace(openai_api_key=""))
    response = TestClient(app).post("/api/research", json={"topic": "solid-state battery trends"})
    assert response.status_code == 503


def test_research_validates_topic() -> None:
    response = TestClient(app).post("/api/research", json={"topic": "short"})
    assert response.status_code == 422
