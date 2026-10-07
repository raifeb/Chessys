from pathlib import Path
import os
import chess

ROOT_DIR: Path = Path(__file__).resolve().parent
ARTIFACTS_DIR: Path = ROOT_DIR / "artifacts"
BIN_DIR: Path = ROOT_DIR / "bin"
DATA_DIR: Path = ROOT_DIR / "data"

STOCKFISH_PATH: Path = (
    BIN_DIR / "stockfish-windows-x86-64-avx2.exe"
    if (BIN_DIR / "stockfish-windows-x86-64-avx2.exe").is_file()
    else ROOT_DIR.parent / "bin" / "stockfish-windows-x86-64-avx2.exe"
)
MODEL_PATH: Path = ARTIFACTS_DIR / "blunder_calibrated.joblib"
FEATURE_NAMES_PATH: Path = ARTIFACTS_DIR / "feature_names.json"

DEFAULT_SEARCH_DEPTH: int = int(os.getenv("STOCKFISH_DEPTH", "10"))
ENGINE_DEPTH: int = DEFAULT_SEARCH_DEPTH
ENGINE_THREADS: int = int(os.getenv("STOCKFISH_THREADS", "1"))
ENGINE_HASH_MB: int = int(os.getenv("STOCKFISH_HASH_MB", "32"))

BLUNDER_THRESHOLD_CP: int = 200
BLUNDER_THRESHOLD_PROB: float = 0.18

MOVE_THRESHOLDS: dict[str, int] = {
    "Best Move": 20,
    "Good": 60,
    "Inaccuracy": 150,
    "Mistake": 300,
}

PIECE_VALUES: dict[chess.PieceType, int] = {
    chess.PAWN: 1,
    chess.KNIGHT: 3,
    chess.BISHOP: 3,
    chess.ROOK: 5,
    chess.QUEEN: 9,
    chess.KING: 0,
}

MOVE_DESCRIPTIONS: dict[str, str] = {
    "Brilliant": "Pengorbanan perwira spektakuler yang mempertahankan atau memperbesar keunggulan posisi.",
    "Great": "Temuan langkah krusial; satu-satunya kelanjutan viable yang mempertahankan ekuitas posisi.",
    "Best Move": "Rekomendasi optimal engine dengan ekuitas posisi maksimal.",
    "Good": "Langkah solid dan sehat dengan degradasi strategis minimal hingga nol.",
    "Inaccuracy": "Langkah suboptimal yang memberikan sedikit inisiatif kepada lawan.",
    "Mistake": "Kesalahan nyata yang secara signifikan mendegradasi ekuitas posisi.",
    "Blunder": "Keteledoran fatal yang menyebabkan kerugian material besar atau posisi kalah.",
}

MOVE_COLORS: dict[str, str] = {
    "Brilliant": "#000000cc",
    "Great": "#000000cc",
    "Best Move": "#333333cc",
    "Good": "#555555cc",
    "Inaccuracy": "#777777cc",
    "Mistake": "#999999cc",
    "Blunder": "#cccccccc",
}


def check_system_readiness() -> dict[str, bool]:
    return {
        "stockfish": STOCKFISH_PATH.is_file(),
        "model": MODEL_PATH.is_file(),
        "feature_names": FEATURE_NAMES_PATH.is_file(),
    }
