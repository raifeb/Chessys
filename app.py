import logging
from typing import Any, Optional
import chess
import chess.engine
import joblib
import streamlit as st

from config import (
    STOCKFISH_PATH,
    MODEL_PATH,
    ENGINE_THREADS,
    ENGINE_HASH_MB,
)
from src.classify import analyze_game_pipeline
from ui.sidebar import render_sidebar
from ui.board_view import render_board_view
from ui.telemetry_view import render_telemetry_view
from ui.match_summary import render_match_summary

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Chessys")

st.set_page_config(
    page_title="Chessys | ML Tactical Telemetry",
    layout="wide",
    initial_sidebar_state="expanded",
)


@st.cache_resource(show_spinner=False)
def load_engine() -> Optional[chess.engine.SimpleEngine]:
    if not STOCKFISH_PATH.is_file():
        logger.warning("Stockfish binary tidak ditemukan di: %s", STOCKFISH_PATH)
        return None

    try:
        engine = chess.engine.SimpleEngine.popen_uci(str(STOCKFISH_PATH))
        engine.configure({"Threads": ENGINE_THREADS, "Hash": ENGINE_HASH_MB})
        return engine
    except Exception as err:
        logger.error("Gagal menginisialisasi Stockfish: %s", err)
        return None


@st.cache_resource(show_spinner=False)
def load_model() -> Optional[Any]:
    if not MODEL_PATH.is_file():
        logger.warning("Artefak model tidak ditemukan di: %s", MODEL_PATH)
        return None

    try:
        return joblib.load(MODEL_PATH)
    except Exception as err:
        logger.error("Gagal memuat model Machine Learning: %s", err)
        return None


@st.cache_data(show_spinner=False)
def run_analysis_pipeline(
    pgn_text: str,
) -> tuple[dict[str, str], list[dict[str, Any]]]:
    engine = load_engine()
    model = load_model()
    return analyze_game_pipeline(pgn_text, engine=engine, model=model)


def init_session_state() -> None:
    state_defaults: dict[str, Any] = {
        "positions": [],
        "headers": {},
        "current_ply": 0,
        "flipped": False,
    }
    for key, default_val in state_defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default_val


def handle_new_pgn(pgn_text: str) -> bool:
    headers, positions = run_analysis_pipeline(pgn_text)
    if positions:
        st.session_state.headers = headers
        st.session_state.positions = positions
        st.session_state.current_ply = 0
        return True

    st.sidebar.error("Notasi PGN tidak valid atau tidak memiliki daftar langkah.")
    return False


def main() -> None:
    st.markdown("""
        <style>
        /* Custom B&W Theme CSS */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;800&display=swap');
        html, body, [class*="css"]  {
            font-family: 'Inter', sans-serif !important;
        }
        .stButton>button {
            border: 2px solid #000;
            border-radius: 8px;
            color: #000;
            background-color: #fff;
            transition: all 0.2s ease-in-out;
            font-weight: 600;
        }
        .stButton>button:hover {
            background-color: #000;
            color: #fff;
        }
        div[data-testid="stMetricValue"] {
            font-size: 1.8rem;
            font-weight: 800;
        }
        h1, h2, h3, h4, h5, h6 {
            font-family: 'Inter', sans-serif !important;
            font-weight: 800 !important;
            color: #000;
            letter-spacing: -0.02em;
        }
        hr {
            border-color: #000 !important;
            opacity: 0.1;
        }
        .stAlert {
            background-color: #f8f9fa;
            border-left: 4px solid #000;
            color: #000;
        }
        </style>
    """, unsafe_allow_html=True)
    
    init_session_state()
    render_sidebar(on_analyze_callback=handle_new_pgn)

    positions: list[dict[str, Any]] = st.session_state.positions
    if not positions:
        st.info("Buka sidebar di kiri atas dan masukkan notasi PGN (atau klik **Load Demo**) untuk memulai telemetri.")
        return

    total_ply = len(positions)
    current_ply = min(max(0, st.session_state.current_ply), total_ply - 1)
    st.session_state.current_ply = current_ply
    active_node = positions[current_ply]

    col_board, col_telemetry = st.columns([5, 7], gap="medium")

    with col_board:
        render_board_view(
            node=active_node,
            headers=st.session_state.headers,
            total_ply=total_ply,
        )

    with col_telemetry:
        render_telemetry_view(
            node=active_node,
            positions=positions,
            current_ply=current_ply,
        )

    st.markdown("---")
    render_match_summary(
        headers=st.session_state.headers,
        positions=positions,
    )


if __name__ == "__main__":
    main()
