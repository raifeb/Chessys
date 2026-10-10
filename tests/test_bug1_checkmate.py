import chess.engine
import pytest
from config import STOCKFISH_PATH
from src.classify import score_to_cp, analyze_game_pipeline
from src.summary import calculate_player_stats

FOOLS_MATE_PGN = """[Event "Fool's Mate"]
[White "White"]
[Black "Black"]
[Result "0-1"]

1. f3 e5 2. g4 Qh4# 0-1"""


def test_score_to_cp_unit():
    # Mate(+n) -> +10000
    assert score_to_cp(chess.engine.Mate(1)) == 10000
    assert score_to_cp(chess.engine.Mate(5)) == 10000
    # Mate(-n) -> -10000
    assert score_to_cp(chess.engine.Mate(-1)) == -10000
    assert score_to_cp(chess.engine.Mate(-3)) == -10000
    # Mate(0) / mated on board -> -10000
    assert score_to_cp(chess.engine.Mate(0)) == -10000
    # MateGiven / delivered mate -> +10000
    assert score_to_cp(chess.engine.MateGiven) == 10000
    # Cp(0) must return 0, not fall back to default via `0 or default`
    assert score_to_cp(chess.engine.Cp(0), default=20) == 0


def test_fools_mate_invariants():
    assert STOCKFISH_PATH.is_file(), f"Stockfish not found at {STOCKFISH_PATH}"
    cap = 1000
    with chess.engine.SimpleEngine.popen_uci(str(STOCKFISH_PATH)) as engine:
        _, positions = analyze_game_pipeline(FOOLS_MATE_PGN, engine=engine, model=None)

    game_moves = [p for p in positions if p["ply"] > 0]
    assert len(game_moves) == 4

    for node in game_moves:
        cp_loss = node["cp_loss"]
        # Invariant 1: 0 <= cp_loss <= cap
        assert 0 <= cp_loss <= cap, f"ply {node['ply']} ({node['san']}) cp_loss={cp_loss} out of [0, {cap}]"
        # Invariant 2: uci == best_move_uci -> cp_loss == 0
        if node["best_move_uci"] and node["uci"] == node["best_move_uci"]:
            assert cp_loss == 0, f"ply {node['ply']} played best_move_uci {node['uci']} but got cp_loss={cp_loss}"

    # Invariant 3: checkmate move Qh4# is not Blunder and winner accuracy > 0
    mate_node = game_moves[-1]
    assert mate_node["san"] == "Qh4#"
    assert mate_node["label"] != "Blunder"
    assert mate_node["cp_loss"] == 0

    black_moves = [p for p in game_moves if p["is_white"] == 0]
    black_stats = calculate_player_stats(black_moves)
    assert black_stats["accuracy"] > 0.0
