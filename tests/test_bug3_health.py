from pathlib import Path
from fastapi.testclient import TestClient
import api


def test_health_endpoint_ok():
    with TestClient(api.app) as client:
        resp = client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert set(data.keys()) >= {"status", "engine_available", "model_loaded"}
        assert data["status"] == "ok"
        assert isinstance(data["engine_available"], bool)
        assert data["model_loaded"] is True


def test_health_endpoint_without_engine(monkeypatch):
    monkeypatch.setattr(api, "STOCKFISH_PATH", Path("/nonexistent/stockfish"))
    with TestClient(api.app) as client:
        resp = client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"
        assert data["engine_available"] is False
        assert data["model_loaded"] is True
