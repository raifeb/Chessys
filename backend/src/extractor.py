import chess

FEATURE_COLS = [
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

PIECE_VALUES = {
    chess.PAWN: 1,
    chess.KNIGHT: 3,
    chess.BISHOP: 3,
    chess.ROOK: 5,
    chess.QUEEN: 9,
    chess.KING: 0,
}

def calculate_material_balance(board: chess.Board, turn: chess.Color) -> int:
    turn_material = sum(
        len(board.pieces(pt, turn)) * val for pt, val in PIECE_VALUES.items()
    )
    opp_material = sum(
        len(board.pieces(pt, not turn)) * val for pt, val in PIECE_VALUES.items()
    )
    return turn_material - opp_material


def calculate_king_openness(board: chess.Board, turn: chess.Color) -> int:
    king_sq = board.king(turn)
    if king_sq is None:
        return 8

    king_surroundings = chess.SquareSet(chess.BB_KING_ATTACKS[king_sq])
    friendly_pawns = board.pieces(chess.PAWN, turn)
    pawn_shields = len(king_surroundings & friendly_pawns)
    return len(king_surroundings) - pawn_shields


def calculate_mobility(board: chess.Board) -> tuple[int, float]:
    legal_turn = board.legal_moves.count()

    # Thread-safe copy instead of mutating board state
    board_copy = board.copy()
    board_copy.turn = not board_copy.turn
    legal_opp = board_copy.legal_moves.count()

    ratio = float(legal_turn) / float(legal_opp + 1)
    return legal_turn, ratio


def extract_features(board: chess.Board, player_elo: int, ply: int) -> dict:
    turn = board.turn
    legal_moves, mobility_ratio = calculate_mobility(board)
    
    # O(N) Single-pass loop for tactical features
    tension = 0
    hanging = 0
    absolute_pins = 0
    
    for sq, piece in board.piece_map().items():
        # Tactical tension
        opp_attackers = board.attackers(not piece.color, sq)
        if opp_attackers:
            tension += len(opp_attackers)
            
        # Hanging pieces and pins
        if piece.color == turn and piece.piece_type != chess.KING:
            is_attacked = bool(board.attackers(not turn, sq))
            is_defended = bool(board.attackers(turn, sq))
            if is_attacked and not is_defended:
                hanging += 1
                
            if board.is_pinned(turn, sq):
                absolute_pins += 1

    return {
        "material_balance": calculate_material_balance(board, turn),
        "tactical_tension": tension,
        "hanging_pieces": hanging,
        "king_openness": calculate_king_openness(board, turn),
        "legal_moves_count": legal_moves,
        "mobility_ratio": mobility_ratio,
        "is_check": int(board.is_check()),
        "absolute_pins": absolute_pins,
        "has_queen_turn": int(bool(board.pieces(chess.QUEEN, turn))),
        "has_queen_opp": int(bool(board.pieces(chess.QUEEN, not turn))),
        "player_elo": int(player_elo),
        "ply": int(ply),
    }

