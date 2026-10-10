from pathlib import Path
from fastapi.testclient import TestClient
import api
from src.classify import analyze_game_pipeline
from src.summary import calculate_player_stats

FOOLS_MATE_PGN = """[Event "Fool's Mate"]
[White "White"]
[Black "Black"]
[Result "0-1"]

1. f3 e5 2. g4 Qh4# 0-1"""


def test_pipeline_without_engine():
    _, positions = analyze_game_pipeline(FOOLS_MATE_PGN, engine=None, model=None)
    game_moves = [p for p in positions if p["ply"] > 0]
    assert len(game_moves) == 4

    for node in game_moves:
        assert node["cp_loss"] is None, f"Expected cp_loss=None without engine, got {node['cp_loss']}"
        assert node["label"] in (None, "Unevaluated"), f"Expected Unevaluated/None label, got {node['label']}"

    white_moves = [p for p in game_moves if p["is_white"] == 1]
    black_moves = [p for p in game_moves if p["is_white"] == 0]
    w_stats = calculate_player_stats(white_moves)
    b_stats = calculate_player_stats(black_moves)

    assert w_stats["acpl"] is None
    assert w_stats["accuracy"] is None
    assert b_stats["acpl"] is None
    assert b_stats["accuracy"] is None


def test_analyze_pgn_endpoint_without_engine_and_not_cached(monkeypatch):
    real_sf = api.STOCKFISH_PATH
    monkeypatch.setattr(api, "STOCKFISH_PATH", Path("/nonexistent/stockfish_missing_bin"))

    with TestClient(api.app) as client:
        resp = client.post("/api/analyze-pgn", json={"pgn": FOOLS_MATE_PGN})
        assert resp.status_code == 200
        data = resp.json()

        assert data.get("engine_available") is False
        for node in data["positions"]:
            if node["ply"] > 0:
                assert node["cp_loss"] is None
                assert node["label"] in (None, "Unevaluated")

        assert data["summary"]["white_stats"]["acpl"] is None
        assert data["summary"]["white_stats"]["accuracy"] is None
        assert data["summary"]["black_stats"]["acpl"] is None
        assert data["summary"]["black_stats"]["accuracy"] is None

        # Restore real engine path and ensure the previous no-engine result was NOT cached as valid
        if real_sf.is_file():
            monkeypatch.setattr(api, "STOCKFISH_PATH", real_sf)
            resp_valid = client.post("/api/analyze-pgn", json={"pgn": FOOLS_MATE_PGN})
            assert resp_valid.status_code == 200
            data_valid = resp_valid.json()
            assert data_valid.get("engine_available") is True
            assert data_valid["summary"]["white_stats"]["accuracy"] is not None
