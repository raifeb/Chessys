# CHESSYS

CHESSYS is a chess analysis web application and machine learning pipeline that evaluates board positions and predicts the empirical probability of a blunder. It combines deterministic tactical feature extraction, a calibrated gradient boosting model, and an interactive full-stack interface with move-by-move telemetry.

## Features

- **Interactive Board Telemetry**: Play moves directly on the board to inspect live tactical metrics and predict blunder probability in real time.
- **PGN Match Analysis**: Upload a `.pgn` game file or load a built-in demo match (Adolf Anderssen vs. Lionel Kieseritzky, 1851) to analyze an entire game.
- **Move Navigation**: Step through moves using playback buttons, a timeline slider, the move notation list, or by clicking nodes directly on the telemetry charts.
- **Dual Telemetry Charts**: Visualizes evaluation advantage (in pawns) and blunder risk percentage across every ply using synchronized charts.
- **Tactical Complexity Metrics**: Computes center tension, hanging pieces, material balance, and move quality labels (Best Move, Good, Inaccuracy, Mistake, Blunder).
- **Post-Match Summary**: Displays player accuracy percentages, Average Centipawn Loss (ACPL), error distribution across phases (Opening, Middlegame, Endgame), and an algorithmic match summary narrative.
- **Stockfish Engine Integration**: Evaluates positions and computes centipawn loss via UCI protocol when the Stockfish binary is present, with graceful fallback to ML-only mode if unavailable.

## Tech Stack

### Frontend
- **Framework**: React 19
- **Language**: TypeScript
- **Build Tool**: Vite
- **Styling**: Tailwind CSS (custom monochrome clay theme)
- **Chess Libraries**: `react-chessboard` (board UI), `chess.js` (move validation and FEN state)
- **Charts**: Recharts
- **Icons**: Lucide React

### Backend
- **Framework**: FastAPI
- **Language**: Python 3.12
- **Server**: Uvicorn
- **Data Validation**: Pydantic v2
- **Chess Library**: `python-chess` (board representation, move generation, attack detection, PGN parsing, UCI engine communication)
- **Chess Engine**: Stockfish (optional local UCI binary)

### Machine Learning
- **Model**: XGBoost (`XGBClassifier`)
- **Calibration**: Scikit-learn (`CalibratedClassifierCV` with Platt scaling / Sigmoid)
- **Data Processing**: Pandas, NumPy
- **Serialization**: Joblib
- **Exploration & Training**: Jupyter Notebooks

## Architecture

```
Frontend (React + Vite)
       │
       │ HTTP / JSON
       ▼
Backend API (FastAPI)
       │
       ├── Tactical Feature Extractor (python-chess)
       ├── ML Inference (Calibrated XGBoost)
       └── Engine Analysis (Stockfish via UCI, optional)
```

## Project Structure

```text
.
├── backend/
│   ├── api.py               # FastAPI application and route definitions
│   ├── config.py            # Engine, paths, and threshold configurations
│   ├── requirements.txt     # Python backend dependencies
│   ├── artifacts/
│   │   ├── blunder_calibrated.joblib  # Production calibrated model
│   │   ├── blunder_xgb_raw.joblib     # Base trained XGBoost model
│   │   ├── feature_names.json         # Input feature list
│   │   └── model_config.json          # Threshold and calibration metadata
│   └── src/
│       ├── classify.py      # Game analysis pipeline and move classification
│       ├── extractor.py     # Deterministic tactical feature extraction
│       └── summary.py       # ACPL, accuracy, and post-match narrative logic
├── frontend/
│   ├── package.json         # Frontend dependencies and scripts
│   ├── vite.config.ts       # Vite build configuration
│   ├── tailwind.config.js   # Tailwind theme with clay elevation styles
│   └── src/
│       ├── App.tsx          # Main application layout and state
│       ├── components/
│       │   ├── BoardControls.tsx      # Navigation slider, buttons, and ply indicator
│       │   ├── ChessBoard.tsx         # Interactive board and toolbar
│       │   ├── MatchHeader.tsx        # Player names, ratings, and avatar fallback
│       │   ├── MatchSummaryView.tsx   # Post-mortem analysis panel
│       │   ├── MetricCard.tsx         # Metric display card
│       │   ├── MoveList.tsx           # Formatted turn-by-turn move list
│       │   ├── Sidebar.tsx            # Actions, upload, demo, and mode selector
│       │   ├── TelemetryChart.tsx     # Recharts eval and risk visualizations
│       │   └── TelemetryPanel.tsx     # Telemetry tabs and metric container
│       ├── hooks/
│       │   └── useChess.ts            # Chess state wrapper around chess.js
│       ├── services/
│       │   └── api.ts                 # HTTP client for backend endpoints
│       └── types/
│           └── index.ts               # Shared TypeScript data types
├── notebooks/
│   ├── 1_eda.ipynb          # Exploratory Data Analysis
│   ├── 2_preprocess.ipynb   # Feature extraction and dataset partitioning
│   ├── 3_model.ipynb        # Model training, class weighting, and threshold tuning
│   └── 4_eval.ipynb         # Probability calibration and Brier score evaluation
├── bin/                     # Local Stockfish executable directory (optional)
└── README.md
```

## Getting Started

### Prerequisites
- Python 3.10+ (tested on Python 3.12)
- Node.js 18+ and npm
- *(Optional)* Stockfish binary placed in `bin/` or `backend/bin/` (e.g. `stockfish-windows-x86-64-avx2.exe`)

### 1. Backend Setup

```bash
cd backend

# Create and activate a virtual environment
python -m venv venv

# Windows:
venv\Scripts\activate
# Linux / macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start the API server
uvicorn api:app --reload --port 8000
```

The backend server runs at `http://localhost:8000`. Interactive OpenAPI documentation is accessible at `http://localhost:8000/docs`.

### 2. Frontend Setup

In a separate terminal:

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

The frontend application runs at `http://localhost:5173`.

To create a production build:

```bash
npm run build
```

## API

The backend exposes three REST endpoints:

- `POST /api/evaluate`
  Evaluates a single board position from a FEN string, player Elo rating, and ply count. Returns the predicted blunder probability, binary blunder decision, and the 12 extracted tactical features.
- `POST /api/evaluate/batch`
  Evaluates an array of FEN strings in a single request. Returns predictions and extracted features for each position.
- `POST /api/analyze-pgn`
  Receives a full PGN string and runs the end-to-end game pipeline. Returns parsed game headers, ply-by-ply evaluations (centipawn loss, move classification, best move, and blunder risk), and aggregated post-match summary statistics.

## Machine Learning

### Features
The model operates on 12 deterministic features extracted from the board state using `python-chess`:
- `material_balance`: Net piece value difference relative to active player.
- `tactical_tension`: Number of active attackers on squares occupied by opponent pieces.
- `hanging_pieces`: Number of undefended friendly pieces under attack.
- `king_openness`: King exposure based on surrounding squares and friendly pawn shields.
- `legal_moves_count`: Total valid moves available to the active player.
- `mobility_ratio`: Ratio of active player's legal moves to opponent's legal moves.
- `is_check`: Binary flag indicating if the king is currently in check.
- `absolute_pins`: Count of friendly pieces pinned to the king.
- `has_queen_turn`: Binary indicator for queen presence on the active side.
- `has_queen_opp`: Binary indicator for queen presence on the opponent side.
- `player_elo`: Elo rating of the active player.
- `ply`: Half-move index (serves as a proxy for game phase).

### Model & Training
- **Algorithm**: `XGBClassifier` trained on game positions derived from rated Lichess games.
- **Class Imbalance**: Managed using positive class weighting (`scale_pos_weight`) during training.
- **Threshold Optimization**: Decision threshold tuned on the validation set targeting $F_2$-score to prioritize blunder detection.
- **Probability Calibration**: Calibrated using Platt Scaling (`CalibratedClassifierCV(method='sigmoid', cv=5)`), achieving a Brier score of ~0.088 on the test set.

## Current Status

- Core telemetry, board interaction, and PGN analysis workflows are fully functional.
- Stockfish evaluation is operational when the binary is present; fallback to ML-only mode is supported.
- Model artifacts (`blunder_calibrated.joblib`, `model_config.json`, `feature_names.json`) are checked in under `backend/artifacts/`.
