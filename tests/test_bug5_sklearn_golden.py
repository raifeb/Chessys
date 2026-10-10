import random
import warnings
from pathlib import Path
import chess
import joblib
import pandas as pd
from sklearn.exceptions import InconsistentVersionWarning
from src.extractor import extract_features, FEATURE_COLS

REPO_ROOT = Path(__file__).resolve().parent.parent
MODEL_PATH = REPO_ROOT / "backend" / "artifacts" / "blunder_calibrated.joblib"
REQUIREMENTS_PATH = REPO_ROOT / "backend" / "requirements.txt"

GOLDEN_PROBS_10 = [
    0.047988495975732806,
    0.05541251078248024,
    0.06095160692930222,
    0.06350716650485992,
    0.06256667673587799,
    0.05570641979575157,
    0.047594272345304486,
    0.04331986680626869,
    0.04434212595224381,
    0.04375722035765648,
]


def test_requirements_pins_sklearn_1_9_0():
    req_text = REQUIREMENTS_PATH.read_text(encoding="utf-8")
    assert "scikit-learn==1.9.0" in req_text


def test_model_loads_without_inconsistent_version_warning_and_matches_golden():
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always", InconsistentVersionWarning)
        model = joblib.load(MODEL_PATH)

    inconsistent_warnings = [
        w for w in caught if issubclass(w.category, InconsistentVersionWarning)
    ]
    assert not inconsistent_warnings, (
        f"Expected no InconsistentVersionWarning, got: {[str(w.message) for w in inconsistent_warnings]}"
    )

    rng = random.Random(42)
    rows = []
    board = chess.Board()
    for ply in range(1, 11):
        elo = 1200 + (len(rows) % 10) * 100
        rows.append(extract_features(board, player_elo=elo, ply=ply))
        move = rng.choice(list(board.legal_moves))
        board.push(move)

    df = pd.DataFrame(rows)[FEATURE_COLS]
    probs = model.predict_proba(df)[:, 1].tolist()

    for idx, (actual, expected) in enumerate(zip(probs, GOLDEN_PROBS_10)):
        assert abs(actual - expected) < 1e-6, (
            f"Row {idx} mismatch: actual={actual} vs expected={expected}"
        )

