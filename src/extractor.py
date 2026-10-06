from typing import Any
import chess
import pandas as pd

from config import PIECE_VALUES

FEATURE_COLS: list[str] = [
    "material_balance",
    "tactical_tension",
    "hanging_pieces",
    "king_openness",
    "legal_moves_count",
    "mobility_ratio",
    "is_check",
    "absolute_pins",
    "has_queen_turn",
    "has_queen_opp",
    "player_elo",
    "ply",
]


def calculate_material_balance(board: chess.Board, turn: chess.Color) -> int:
    turn_material = sum(
        len(board.pieces(pt, turn)) * val for pt, val in PIECE_VALUES.items()
    )
    opp_material = sum(
        len(board.pieces(pt, not turn)) * val for pt, val in PIECE_VALUES.items()
    )
    return turn_material - opp_material


def calculate_tactical_tension(board: chess.Board) -> int:
    tension = 0
    for sq, piece in board.piece_map().items():
        opp_attackers = board.attackers(not piece.color, sq)
        if opp_attackers:
            tension += len(opp_attackers)
    return tension


def calculate_hanging_pieces(board: chess.Board, turn: chess.Color) -> int:
    hanging = 0
    for sq, piece in board.piece_map().items():
        if piece.color == turn and piece.piece_type != chess.KING:
            is_attacked = bool(board.attackers(not turn, sq))
            is_defended = bool(board.attackers(turn, sq))
            if is_attacked and not is_defended:
                hanging += 1
    return hanging


def calculate_king_openness(board: chess.Board, turn: chess.Color) -> int:
    king_sq = board.king(turn)
    if king_sq is None:
        return 8

    king_surroundings = chess.SquareSet(chess.BB_KING_ATTACKS[king_sq])
    friendly_pawns = board.pieces(chess.PAWN, turn)
    pawn_shields = len(king_surroundings & friendly_pawns)
    return len(king_surroundings) - pawn_shields


def calculate_absolute_pins(board: chess.Board, turn: chess.Color) -> int:
    pinned_count = 0
    for sq, piece in board.piece_map().items():
        if piece.color == turn and piece.piece_type != chess.KING:
            if board.is_pinned(turn, sq):
                pinned_count += 1
    return pinned_count


def calculate_mobility(board: chess.Board) -> tuple[int, float]:
    legal_turn = board.legal_moves.count()

    board.turn = not board.turn
    try:
        legal_opp = board.legal_moves.count()
    finally:
        board.turn = not board.turn

    ratio = float(legal_turn) / float(legal_opp + 1)
    return legal_turn, ratio


def extract_features(board: chess.Board, player_elo: int, ply: int) -> dict[str, Any]:
    turn = board.turn
    legal_moves, mobility_ratio = calculate_mobility(board)

    return {
        "material_balance": calculate_material_balance(board, turn),
        "tactical_tension": calculate_tactical_tension(board),
        "hanging_pieces": calculate_hanging_pieces(board, turn),
        "king_openness": calculate_king_openness(board, turn),
        "legal_moves_count": legal_moves,
        "mobility_ratio": mobility_ratio,
        "is_check": int(board.is_check()),
        "absolute_pins": calculate_absolute_pins(board, turn),
        "has_queen_turn": int(bool(board.pieces(chess.QUEEN, turn))),
        "has_queen_opp": int(bool(board.pieces(chess.QUEEN, not turn))),
        "player_elo": int(player_elo),
        "ply": int(ply),
    }


def features_to_dataframe(feature_dict: dict[str, Any]) -> pd.DataFrame:
    return pd.DataFrame([feature_dict])[FEATURE_COLS]


_calculate_material_balance = calculate_material_balance
_calculate_tactical_tension = calculate_tactical_tension
_calculate_hanging_pieces = calculate_hanging_pieces
_calculate_king_openness = calculate_king_openness
_calculate_absolute_pins = calculate_absolute_pins
_calculate_mobility = calculate_mobility
