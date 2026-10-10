import io
import logging
from typing import Any, Optional
import chess
import chess.engine
import chess.pgn
import pandas as pd

from config import (
    ENGINE_DEPTH,
    MOVE_THRESHOLDS,
)
from src.extractor import extract_features, FEATURE_COLS

logger = logging.getLogger(__name__)


CP_LOSS_CAP: int = 1000


def score_to_cp(score: chess.engine.Score, default: int = 0) -> int:
    if score.is_mate():
        if score == chess.engine.MateGiven:
            return 10000
        mate_moves = score.mate()
        return 10000 if (mate_moves is not None and mate_moves > 0) else -10000
    val = score.score(mate_score=10000)
    return default if val is None else val


def classify_move(cp_loss: int) -> str:
    for label, threshold in MOVE_THRESHOLDS.items():
        if cp_loss <= threshold:
            return label
    return "Blunder"


def analyze_game_pipeline(
    pgn_text: str,
    engine: Optional[chess.engine.SimpleEngine],
    model: Optional[Any],
) -> tuple[dict[str, str], list[dict[str, Any]]]:
    pgn_io = io.StringIO(pgn_text.strip())
    game = chess.pgn.read_game(pgn_io)
    if not game:
        return {}, []

    headers: dict[str, str] = {
        "white": game.headers.get("White", "White Player"),
        "black": game.headers.get("Black", "Black Player"),
        "white_elo": game.headers.get("WhiteElo", "1500"),
        "black_elo": game.headers.get("BlackElo", "1500"),
        "opening": game.headers.get("Opening", "Standard Opening"),
        "eco": game.headers.get("ECO", "-"),
    }

    board = game.board()
    positions: list[dict[str, Any]] = []

    current_eval_info: Optional[chess.engine.InfoDict] = None
    eval_cp_white: Optional[int] = None

    if engine is not None:
        try:
            current_eval_info = engine.analyse(
                board, chess.engine.Limit(depth=ENGINE_DEPTH)
            )
            eval_cp_white = score_to_cp(current_eval_info["score"].white(), default=20)
        except Exception as err:
            logger.warning("Gagal menganalisis posisi awal dengan Stockfish: %s", err)
            current_eval_info = None

    root_node: dict[str, Any] = {
        "ply": 0,
        "move_number": 1,
        "color": "white",
        "is_white": 1,
        "san": "Initial",
        "uci": "",
        "from_sq": None,
        "to_sq": None,
        "fen": board.fen(),
        "eval_cp": eval_cp_white,
        "cp_eval_white": eval_cp_white,
        "cp_loss": 0 if current_eval_info is not None else None,
        "label": "Best Move" if current_eval_info is not None else "Unevaluated",
        "risk_prob": 0.0,
        "blunder_risk_pct": 0.0,
        "best_move": "-",
        "best_move_uci": None,
        "tactical_tension": 0,
        "hanging_pieces": 0,
        "material_balance": 0,
        "features": {},
    }
    positions.append(root_node)

    all_raw_features: list[dict[str, Any]] = []
    moves = list(game.mainline_moves())

    for ply_idx, move in enumerate(moves, start=1):
        turn = board.turn
        color_str = "white" if turn == chess.WHITE else "black"
        current_elo_str = (
            headers["white_elo"] if turn == chess.WHITE else headers["black_elo"]
        )
        try:
            current_elo = int(current_elo_str)
        except ValueError:
            current_elo = 1500

        move_number = (ply_idx + 1) // 2

        raw_features = extract_features(board, player_elo=current_elo, ply=ply_idx)
        all_raw_features.append(raw_features)

        best_move_san = "-"
        best_move_uci = None
        eval_before_turn = 0

        if current_eval_info is not None:
            pv = current_eval_info.get("pv", [])
            if pv:
                best_move_obj = pv[0]
                best_move_uci = best_move_obj.uci()
                try:
                    best_move_san = board.san(best_move_obj)
                except ValueError:
                    best_move_san = best_move_uci

            eval_before_turn = score_to_cp(current_eval_info["score"].pov(turn))

        from_sq_str = chess.square_name(move.from_square)
        to_sq_str = chess.square_name(move.to_square)
        san_str = board.san(move)
        uci_str = move.uci()
        board.push(move)

        cp_loss: Optional[int] = None
        cp_eval_white: Optional[int] = None
        next_eval_info: Optional[chess.engine.InfoDict] = None

        if engine is not None:
            try:
                next_eval_info = engine.analyse(
                    board, chess.engine.Limit(depth=ENGINE_DEPTH)
                )
                eval_after_turn = score_to_cp(next_eval_info["score"].pov(turn))
                if best_move_uci is not None and uci_str == best_move_uci:
                    cp_loss = 0
                else:
                    cp_loss = min(CP_LOSS_CAP, max(0, eval_before_turn - eval_after_turn))
                cp_eval_white = score_to_cp(next_eval_info["score"].white())
            except Exception as err:
                logger.warning("Gagal menganalisis ply %d: %s", ply_idx, err)
                next_eval_info = None

        current_eval_info = next_eval_info
        label = classify_move(cp_loss) if cp_loss is not None else "Unevaluated"

        node: dict[str, Any] = {
            "ply": ply_idx,
            "move_number": move_number,
            "color": color_str,
            "is_white": int(turn == chess.WHITE),
            "san": san_str,
            "uci": uci_str,
            "from_sq": from_sq_str,
            "to_sq": to_sq_str,
            "fen": board.fen(),
            "eval_cp": cp_eval_white,
            "cp_eval_white": cp_eval_white,
            "cp_loss": cp_loss,
            "label": label,
            "risk_prob": 0.0,
            "blunder_risk_pct": 0.0,
            "best_move": best_move_san,
            "best_move_uci": best_move_uci,
            "tactical_tension": raw_features.get("tactical_tension", 0),
            "hanging_pieces": raw_features.get("hanging_pieces", 0),
            "material_balance": raw_features.get("material_balance", 0),
            "features": raw_features,
        }
        positions.append(node)

    if model is not None and all_raw_features:
        try:
            df_batch = pd.DataFrame(all_raw_features)[FEATURE_COLS]
            pred_probs = model.predict_proba(df_batch)[:, 1]
            for i, prob in enumerate(pred_probs):
                pos_node = positions[i + 1]
                prob_float = float(prob)
                pos_node["risk_prob"] = prob_float
                pos_node["blunder_risk_pct"] = prob_float * 100.0
        except Exception as err:
            logger.warning("Batch ML inference gagal: %s", err)

    return headers, positions
