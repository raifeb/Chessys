import asyncio
from contextlib import asynccontextmanager
from typing import Any, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import joblib
import pandas as pd
import chess
import chess.engine
from pathlib import Path
import json
import logging

from config import STOCKFISH_PATH, ENGINE_THREADS, ENGINE_HASH_MB
from src.extractor import extract_features
from src.classify import analyze_game_pipeline
from src.summary import calculate_player_stats, aggregate_phase_errors, build_narrative

logger = logging.getLogger("ChessysAPI")

# Global state
ml_models: dict[str, Any] = {}
engine_state: dict[str, Optional[chess.engine.SimpleEngine]] = {"engine": None}

ARTIFACTS_DIR = Path(__file__).parent / "artifacts"


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. Load ML Model
    model_path = ARTIFACTS_DIR / "blunder_calibrated.joblib"
    config_path = ARTIFACTS_DIR / "model_config.json"
    
    if not model_path.exists():
        raise RuntimeError(f"Model file not found: {model_path}")
        
    ml_models["model"] = joblib.load(model_path)
    
    with open(config_path, "r") as f:
        config = json.load(f)
    ml_models["config"] = config
    ml_models["features"] = config["features"]
    
    # 2. Init Stockfish Engine if available
    if STOCKFISH_PATH.is_file():
        try:
            engine = chess.engine.SimpleEngine.popen_uci(str(STOCKFISH_PATH))
            engine.configure({"Threads": ENGINE_THREADS, "Hash": ENGINE_HASH_MB})
            engine_state["engine"] = engine
            logger.info("Stockfish engine initialized successfully.")
        except Exception as err:
            logger.warning(f"Could not initialize Stockfish engine: {err}")
            engine_state["engine"] = None
    else:
        logger.info("Stockfish binary not found, running with ML-only mode.")

    yield

    # Cleanup
    if engine_state["engine"]:
        try:
            engine_state["engine"].quit()
        except Exception:
            pass
    ml_models.clear()


app = FastAPI(lifespan=lifespan, title="Chessys API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class EvaluationRequest(BaseModel):
    fen: str = Field(..., description="Forsyth-Edwards Notation of the board")
    player_elo: int = Field(1500, description="Player Elo rating")
    ply: int = Field(20, description="Game ply (half-moves)")


class TelemetryData(BaseModel):
    material_balance: int
    tactical_tension: int
    hanging_pieces: int
    king_openness: int
    legal_moves_count: int
    mobility_ratio: float
    is_check: int
    absolute_pins: int


class EvaluationResponse(BaseModel):
    blunder_probability: float
    is_blunder: bool
    features: TelemetryData


@app.post("/api/evaluate", response_model=EvaluationResponse)
async def evaluate_position(req: EvaluationRequest):
    try:
        board = chess.Board(req.fen)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid FEN string")

    raw_features = extract_features(board, req.player_elo, req.ply)
    model = ml_models["model"]
    feature_names = ml_models["features"]
    threshold = ml_models["config"]["balanced_threshold"]
    
    df = pd.DataFrame([raw_features])[feature_names]
    prob = float(model.predict_proba(df)[0, 1])
    is_blunder = prob >= threshold

    return EvaluationResponse(
        blunder_probability=prob,
        is_blunder=is_blunder,
        features=TelemetryData(**raw_features)
    )


class BatchEvaluationRequest(BaseModel):
    fens: list[str] = Field(..., description="List of FEN strings to evaluate")
    player_elo: int = Field(1500, description="Player Elo rating")


@app.post("/api/evaluate/batch", response_model=list[EvaluationResponse])
async def evaluate_batch(req: BatchEvaluationRequest):
    if not req.fens:
        return []
        
    features_list = []
    for i, fen in enumerate(req.fens):
        try:
            board = chess.Board(fen)
            raw_features = extract_features(board, req.player_elo, i + 1)
            features_list.append(raw_features)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid FEN string at index {i}")

    model = ml_models["model"]
    feature_names = ml_models["features"]
    threshold = ml_models["config"]["balanced_threshold"]
    
    df = pd.DataFrame(features_list)[feature_names]
    probs = model.predict_proba(df)[:, 1]
    
    results = []
    for i, prob in enumerate(probs):
        is_blunder = prob >= threshold
        results.append(EvaluationResponse(
            blunder_probability=float(prob),
            is_blunder=bool(is_blunder),
            features=TelemetryData(**features_list[i])
        ))

    return results


class PgnAnalysisRequest(BaseModel):
    pgn: str = Field(..., description="Full PGN string of the game")


def _run_pipeline(pgn_text: str, model: Any) -> tuple[dict[str, str], list[dict[str, Any]]]:
    engine = None
    if STOCKFISH_PATH.is_file():
        try:
            engine = chess.engine.SimpleEngine.popen_uci(str(STOCKFISH_PATH))
            engine.configure({"Threads": ENGINE_THREADS, "Hash": ENGINE_HASH_MB})
        except Exception as e:
            logger.warning(f"Stockfish engine error: {e}")
            engine = None
            
    try:
        return analyze_game_pipeline(pgn_text, engine=engine, model=model)
    finally:
        if engine:
            try:
                engine.quit()
            except Exception:
                pass


@app.post("/api/analyze-pgn")
async def analyze_pgn_endpoint(req: PgnAnalysisRequest):
    if not req.pgn.strip():
        raise HTTPException(status_code=400, detail="PGN cannot be empty")
        
    try:
        headers, positions = await asyncio.to_thread(
            _run_pipeline,
            req.pgn,
            ml_models.get("model")
        )
    except Exception as e:
        logger.error(f"Error in PGN analysis: {e}")
        raise HTTPException(status_code=400, detail=f"Failed to analyze PGN: {str(e)}")

    if not positions:
        raise HTTPException(status_code=400, detail="Invalid PGN: No valid moves found")

    game_moves = [p for p in positions if p.get("ply", 0) > 0]
    white_moves = [p for p in game_moves if p.get("is_white") == 1]
    black_moves = [p for p in game_moves if p.get("is_white") == 0]

    white_stats = calculate_player_stats(white_moves)
    black_stats = calculate_player_stats(black_moves)

    w_err = aggregate_phase_errors(white_moves)
    b_err = aggregate_phase_errors(black_moves)

    eco = headers.get("eco", "").strip()
    opening = headers.get("opening", "").strip()
    if eco and opening:
        opening_str = f"{eco} - {opening}"
    else:
        opening_str = opening or eco or "Custom / Uncategorized Opening"

    narrative = build_narrative(headers, white_stats, black_stats, w_err, b_err)

    return {
        "headers": headers,
        "positions": positions,
        "summary": {
            "white_stats": white_stats,
            "black_stats": black_stats,
            "white_phase_errors": w_err,
            "black_phase_errors": b_err,
            "narrative": narrative,
            "opening": opening_str
        }
    }
