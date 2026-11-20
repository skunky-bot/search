import json
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


def test_collection_search_uses_reviewed_registry_and_matches_all_terms(tmp_path, monkeypatch):
    registry = tmp_path / "registry.json"
    approved = {"id": "solar", "label": "Cape Town directory", "url": "https://example.org/contacts",
                "tags": ["Solar"], "enabled": True, "mode": "web-collection", "outreach_allowed": False}
    registry.write_text(json.dumps({"sources": [
        {**approved, "id": "preview", "mode": "caller-supplied-html"},
        {**approved, "id": "disabled", "enabled": False},
        approved,
    ]}), encoding="utf-8")
    monkeypatch.setenv("SKUNKY_SOURCE_REGISTRY_PATH", str(registry))
    monkeypatch.setenv("SKUNKY_SERVICE_TOKEN", "test-secret")
    headers = {"X-Skunky-Token": "test-secret"}

    result = client.post("/v1/search", headers=headers, json={
        "query": "  SOLAR cape  ", "limit": 1, "collection_only": True,
    })
    assert result.status_code == 200
    assert result.json()["sources"] == [approved]
    assert client.post("/v1/search", headers=headers, json={
        "query": "solar wind", "collection_only": True,
    }).json()["sources"] == []

    registry.unlink()
    assert client.post("/v1/search", headers=headers, json={"query": "solar"}).status_code == 503
