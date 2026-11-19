import os
from fastapi.testclient import TestClient
from app import app

client = TestClient(app)


def test_search_auth_and_registry(monkeypatch):
    monkeypatch.setenv("SKUNKY_SERVICE_TOKEN", "test-secret")
    assert client.post("/v1/search", json={"query": "example"}).status_code == 401
    response = client.post("/v1/search", headers={"X-Skunky-Token": "test-secret"}, json={"query": "demo"})
    assert response.status_code == 200
    assert response.json()["sources"][0]["id"] == "example-docs"
    assert response.json()["sources"][0]["outreach_allowed"] is False


def test_health():
    assert client.get("/healthz").json()["status"] == "ok"
